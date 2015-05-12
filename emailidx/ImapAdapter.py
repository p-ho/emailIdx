#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#    emailIdx - Synchronizes emails from IMAP to Elasticsearch
#    Copyright (C) 2015 Paul Hofmann
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#########################################################################################
#                                      Imports                                          #
#########################################################################################
from emailidx import EmailSerializer, CertificateVerifier, Settings
from imaplib2 import imaplib2
from M2Crypto import X509
import re, sys
#########################################################################################
#                                 Global Variables                                      #
#########################################################################################
TLS_METHOD = {
              'PLAIN': { 'USE_SSL': False, 'USE_STARTTLS': False },
              'SSL/TLS': { 'USE_SSL': True, 'USE_STARTTLS': False },
              'STARTTLS': { 'USE_SSL': False, 'USE_STARTTLS': True },
              }

IMAP_MAILBOX_DESC_REGEX = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
#########################################################################################
#                                    Exceptions                                         #
#########################################################################################
class NoCertificateFoundError(Exception):
    pass
#########################################################################################
#                                   Helper Functions                                    #
#########################################################################################
def get_peer_certificate_of_connection(imap_connection):
    """
    Returns the certficate of the remote peer.
    If the connection is unencrypted or the certificate can't be found for any other reason, NoCertificateFoundError is raised.
    If the can't be parsed properly, X509Error is raised.
    """
    if hasattr(imap_connection, 'ssl'):
        sock = imap_connection.ssl()
    else:
        sock = imap_connection.sock
    if not hasattr(sock, 'getpeercert'):
        raise NoCertificateFoundError('No certificate found. Is connection really encrypted?')
    data = sock.getpeercert(binary_form=True)
    cert = X509.load_cert_string(data, X509.FORMAT_DER)
    return cert

def verify_connection_security(imap_connection):
    """
    Checks the certificate of the remote peer using the method specified in IMAP_TLS_VERIFY_METHOD in Settings.
    In case the certificate is invalid, emailidx.CertificateVerifier.InsecureCertificateError is raised.
    If no encryption is used (IMAP_TLS_METHOD='PLAIN'), NO check will be performed.
    """
    if Settings.settings['imap']['tls_method'] in ('SSL/TLS', 'STARTTLS'):
        peer_cert = get_peer_certificate_of_connection(imap_connection)
        CertificateVerifier.CERTIFICATE_VERIFY_METHOD[Settings.settings['imap']['tls_verify_method']](peer_cert, Settings.settings['imap']['credentials']['host'])
    

def open_connection():
    """
    Opens IMAP connection and tries to log in as specified in the settings.
    """
    tls_method = TLS_METHOD[Settings.settings['imap']['tls_method']]
    
    if tls_method['USE_SSL']:
        the_port = Settings.settings['imap']['port'] if Settings.settings['imap']['port'] is not None else  imaplib2.IMAP4_SSL_PORT
        imap_connection = imaplib2.IMAP4_SSL(Settings.settings['imap']['credentials']['host'], the_port)
    else:
        the_port = Settings.settings['imap']['port'] if Settings.settings['imap']['port'] is not None else  imaplib2.IMAP4_PORT
        imap_connection = imaplib2.IMAP4(Settings.settings['imap']['credentials']['host'], the_port)
        
    if tls_method['USE_STARTTLS']:
        imap_connection.starttls()
        
    try:
        verify_connection_security(imap_connection)
    except CertificateVerifier.InsecureCertificateError, icerr:
        print >>sys.stderr, "[IMAP] The certicate of the remote peer was not accepted for the following reason:"
        print >>sys.stderr, "[IMAP] \"%s\"" % icerr.message
        sys.exit(-1)
        
    if Settings.settings['imap']['use_cram_transfer']:
        imap_connection.login_cram_md5(Settings.settings['imap']['credentials']['user'], Settings.settings['imap']['credentials']['password'])
    else:
        imap_connection.login(Settings.settings['imap']['credentials']['user'], Settings.settings['imap']['credentials']['password'])
        
    return imap_connection
    
def parse_mailbox_description(mbx_desc_line):
    """
    Parses mailbox name, flags and hierarchy delimiter from the given IMAP-LIST line.
    """
    flags, delimiter, mailbox_name = IMAP_MAILBOX_DESC_REGEX.match(mbx_desc_line).groups()
    mailbox_name = mailbox_name.strip('"')
    flags = [flag_with_slash[1:] for flag_with_slash in flags.split(' ')]
    return { 'flags': flags, 'delimiter': delimiter, 'mailbox_name': mailbox_name }

def get_mailboxes(imap_connection):
    """
    Returns information about all mailboxes.
    """
    (rv, mbx_descs) = imap_connection.list()
    if rv == 'OK':
        mailboxes = []
        for mbx_desc in mbx_descs:
            mailboxes.append(parse_mailbox_description(mbx_desc))
        return mailboxes
    else:
        return None
    
def get_message_in_current_mailbox(imap_connection, message_id):
    """
    Returns the serialized message with the given message_id from the currently selected mailbox.
    """
    rv, msg_data = imap_connection.fetch(message_id, '(RFC822)')
    if rv != 'OK':
        print >>sys.stderr,  "[IMAP] Couldn't fetch message with id %s" % message_id
        return None
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg_as_rfc822 = response_part[1]
            the_email = { 'raw_message': msg_as_rfc822 }
            the_email = EmailSerializer.serialize_email_with_context(the_email)
            if not Settings.settings['sync_behavior']['keep_raw_messages']:
                del the_email['raw_message']
            return the_email
    return None

def get_all_messages_in_mailbox(imap_connection, mailbox_name):
    """
    Get all messages in serialized format from the given mailbox.
    The messages are sorted by their SHA256 hash value.
    """
    rv = imap_connection.select(mailbox_name, readonly=True)[0]
    if rv == 'OK':
        print "[IMAP] Processing mailbox: %s" % mailbox_name
        messages = {}
        rv, data = imap_connection.search(None, "ALL")
        if rv != 'OK':
            # No messages found
            return messages
        msg_ids = data[0].split()
        for msg_id in msg_ids:
            curr_msg = get_message_in_current_mailbox(imap_connection, msg_id)
            if curr_msg:
                curr_msg['mailbox'] = mailbox_name
                curr_msg_hash = curr_msg['hash']
                
                if curr_msg_hash not in messages:
                    messages[curr_msg_hash] = []
                messages[curr_msg_hash].append(curr_msg)
        imap_connection.close()
        return messages
    else:
        print >>sys.stderr,  "[IMAP] Couldn't select mailbox: %s" % mailbox_name
        return None


def fetch_all_emails_from_connection(imap_connection):
    """
    Fetches all emails from the given IMAP connection ordered by mailboxes.
    """
    messages = {}
    for mbx in get_mailboxes(imap_connection):
        mbx_name = mbx['mailbox_name']
        if mbx_name not in Settings.settings['sync_behavior']['excluded_mailboxes']:
            if 'Noselect' not in mbx['flags']:
                msgs_by_hash = get_all_messages_in_mailbox(imap_connection, mbx_name)
                if msgs_by_hash:
                    messages[mbx_name] = msgs_by_hash
    return messages

#########################################################################################
#                                Exposed Functions                                      #
#########################################################################################
def fetch_all_emails_via_imap():
    """
    Fetches all emails from the IMAP server configured in settings ordered by mailboxes.
    """        
    imap_connection = open_connection()
    msgs_by_mailbox = fetch_all_emails_from_connection(imap_connection)
    imap_connection.logout()
    print '[IMAP] logged out.'      
    return msgs_by_mailbox      

