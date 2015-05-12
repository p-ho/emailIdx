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
#                                        Imports                                        #
#########################################################################################
from M2Crypto import SMIME, BIO
from emailidx import SslKeystore,  EmailSerializer
#########################################################################################
#                                   Actual Decryption                                   #
#########################################################################################
def actual_decrypt_message(message, content_type=None, content_transfer_encoding=None):
    
    msg_str = ""
    if content_type is not None:
        msg_str += "Content-Type: %s\r\n" % content_type
    if content_transfer_encoding is not None:
        msg_str += "Content-Transfer-Encoding: %s\r\n" % content_transfer_encoding
    msg_str += "\r\n%s\r\n" % message
    
    msg_buf = BIO.MemoryBuffer(msg_str)
    
    p7 = SMIME.smime_load_pkcs7_bio(msg_buf)[0]
    
    decrypted_data = None
    
    s = SMIME.SMIME()
    
    for key_pair in SslKeystore.keystore:
        s.pkey = key_pair['key']
        s.x509 = key_pair['cert']
                
        try:
            decrypted_data = s.decrypt(p7)
            print "[S/MIME] decrypt with %s : SUCCESS" % key_pair['email']
            break
        except SMIME.PKCS7_Error:
            print "[S/MIME] decrypt with %s : FAILED" % key_pair['email']
            continue
    
    return EmailSerializer.serialize_email_raw_message(decrypted_data) if decrypted_data is not None else None
#########################################################################################
#                                   Exposed Functions                                   #
#########################################################################################
def try_decrypt_smime(message_part, crypto_method):
    message_part['crypto_method'] = crypto_method
    msg_headers = message_part['headers']
    
    content_type = msg_headers['Content-Type'][0] \
                    if ('Content-Type' in msg_headers) and (len(msg_headers['Content-Type']) > 0) \
                    else None
    content_transfer_encoding = msg_headers['Content-Transfer-Encoding'][0] \
                    if ('Content-Transfer-Encoding' in msg_headers) and (len(msg_headers['Content-Transfer-Encoding']) > 0) \
                    else None
    msg_dec = actual_decrypt_message(message_part['content'], content_type, content_transfer_encoding)
    message_part['message_decrypted'] = msg_dec
    message_part['crypto_success'] = msg_dec is not None


def is_smime(message_part, crypto_method):
    content_type = message_part['content_type']
    if 'smime-type' not in content_type:
        return False
    return (content_type['_type'] == 'application/pkcs7-mime') and (content_type['smime-type'] == 'enveloped-data')


def __get_content_filter_functions__(settings):
    return (is_smime, try_decrypt_smime)
    

