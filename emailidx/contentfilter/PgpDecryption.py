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
import gnupg
from emailidx import EmailSerializer
from emailidx.settings import Settings
#########################################################################################
#                                   Actual Decryption                                   #
#########################################################################################
def actual_decrypt_message(message):
    gpg = gnupg.GPG(gnupghome=Settings.GPG_HOME)
    decrypted_data = gpg.decrypt(message)

    return EmailSerializer.serialize_email_raw_message(str(decrypted_data)) \
        if decrypted_data.ok else None
#########################################################################################
#                                   Exposed Functions                                   #
#########################################################################################
def try_decrypt_pgp_mime(message_part, crypto_method):
    if message_part['child_messages'] is not None:
        for child_msg in message_part['child_messages']:
            if 'Content-Description' in child_msg['headers']:
                if child_msg['headers']['Content-Description'] is not None:
                    if "encrypted message" in child_msg['headers']['Content-Description'][0]:
                        child_msg['crypto_method'] = crypto_method
                        if child_msg['content'] is not None:
                            msg_dec = actual_decrypt_message(child_msg['content'])
                            child_msg['message_decrypted'] = msg_dec
                            child_msg['crypto_success'] = msg_dec is not None


def is_pgp_mime(message_part, crypto_method):
    content_type = message_part['content_type']
    if 'protocol' not in content_type:
        return False
    return (content_type['_type'] == 'multipart/encrypted') and (content_type['protocol'] == 'application/pgp-encrypted')


def __get_content_filter_functions__():
    return (is_pgp_mime, try_decrypt_pgp_mime)
    