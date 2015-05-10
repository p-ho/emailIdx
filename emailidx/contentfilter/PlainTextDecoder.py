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
import base64
import quopri
#########################################################################################
#                                   Exposed Functions                                   #
#########################################################################################
def try_filter_plain_text(message_part, filter_method):
    msg_content = message_part['content']
    txt_contents = msg_content
    uses_ctenc = False
    if 'Content-Transfer-Encoding' in message_part['headers']:
        ctenc = message_part['headers']['Content-Transfer-Encoding']
        if 'base64' in ctenc:
            txt_contents = base64.b64decode(msg_content)
            uses_ctenc = True
        elif 'quoted-printable' in ctenc:
            txt_contents = quopri.decodestring(msg_content)
            uses_ctenc = True
        elif 'binary' in ctenc:
            return
            
    if 'charset' in message_part['content_type']:
        txt_contents = txt_contents.decode(message_part['content_type']['charset']).encode('utf-8')
        if not uses_ctenc:
            message_part['content'] = txt_contents
    message_part['content_parsed'] = { 'txt_contents' : txt_contents }


def is_plain_text(message_part, filter_method):
    return message_part['content_type']['_type'].startswith('text/')

def __get_content_filter_functions__(settings):
    return (is_plain_text, try_filter_plain_text)
