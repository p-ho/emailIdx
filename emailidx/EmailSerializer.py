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
import hashlib, re, sys
import email
from email import header
#########################################################################################
#                                 Global Variables                                      #
#########################################################################################
SEMICOLON_WHITESPACE_REGEX = re.compile(r";\s*")

CONTENT_TYPE_MIME_REGEX = re.compile(r"""
    [a-zA-Z0-9_\-\+\.]+
    /
    [a-zA-Z0-9_\-\+\.]+
    """, re.X)

CONTENT_TYPE_PARAM_REGEX = re.compile(r"""
    (?P<key>
        [a-zA-Z0-9_/\-\+\.]+
    )
    [ \t]*
    =
    [ \t]*
    (
        (
        \"
        (?P<value_with_quote>
            [^\"]+
        )
        \"
        )
        |
        (?P<value_without_quote>
            [^ \t\n\r\f\v;]+
        )
    )\s*
    """, re.X)
#########################################################################################
#                                   Helper Functions                                    #
#########################################################################################
def _try_match(re_obj, the_str):
    """
    Tries to match the given RegEx object to the start of the given string
    and returns a tuple containing the match object (or None if no match was found)
    and the trailing string after the matched string part.
    """
    match_obj = re_obj.match(the_str)
    if match_obj is not None:
        match_len = len(match_obj.group(0))
        return (match_obj, the_str[match_len:])
    else:
        return (match_obj, the_str)

def _get_header_entries(serialized_msg, header_name):
    """
    Returns all header lines from the given message by the given key.
    """
    msg_headers = serialized_msg['headers']
    return msg_headers.get(header_name)

def _get_first_header_entry(serialized_msg, header_name):
    """
    Returns the first header line from the given message by the given key.
    """
    header_entries = _get_header_entries(serialized_msg, header_name)
    if (header_entries is not None) and (len(header_entries) > 0):
        return header_entries[0]
    else:
        return None

def _decode_encdoded_words_in_header_list(header_list):
    """
    Takes a list of header attributes and returns a list of those attributes with containing encoded words decoded.
    """
    decoded_header_list = []
    for header_entry in header_list:
        decoded_header_list.append(_decode_encoded_words(header_entry))
    return decoded_header_list


def _decode_encoded_words(header_entry):
    """
    Returns the given header entry with encoded words in decoded format.
    """
    decoded_header_fragments = header.decode_header(header_entry)
    decoded_header = ""
    sep = ""
    for (decoded_string, charset) in decoded_header_fragments:
        out_str = decoded_string if charset is None else decoded_string.decode(charset).encode('utf-8')
        decoded_header += sep + out_str
        sep = " "
    return  decoded_header

def parse_content_types(message_part):
    """
    Get dictionary of content-type preferences from the given serialized message-part.
    """
    content_types = {}
    if 'Content-Type' in message_part['headers']:
        content_type_lists = message_part['headers']['Content-Type']
        for content_type_list in content_type_lists:
            remain_str = content_type_list
            (mime_match, remain_str) = _try_match(CONTENT_TYPE_MIME_REGEX, remain_str)
            if mime_match is not None:
                content_types['_type'] = _decode_encoded_words(mime_match.group(0))
                
                while True:
                    (semicol_match, remain_str) = _try_match(SEMICOLON_WHITESPACE_REGEX, remain_str)
                    if semicol_match is None:
                        break
                    (content_param_match, remain_str) = _try_match(CONTENT_TYPE_PARAM_REGEX, remain_str)
                    if content_param_match is None:
                        break
                    kvpair_dict = content_param_match.groupdict()
                    content_types[kvpair_dict['key']] = \
                        _decode_encoded_words(kvpair_dict['value_with_quote']) \
                        if kvpair_dict['value_with_quote'] is not None else \
                        _decode_encoded_words(kvpair_dict['value_without_quote'])
                    
            if len(remain_str) > 0:
                print >>sys.stderr, "[EMLSERIAL] Unparsable content-type: %s" % content_type_list
                
    if '_type' not in content_types:
        content_types['_type'] = 'unknown/unknown'
    return content_types
#########################################################################################
#                                Exposed Functions                                      #
#########################################################################################
def serialize_email_message(email_msg):
    """
    Convert the given email object to a serializable dictionary representation.
    """
    the_payload_primitive = None
    the_payload_complex = None
    if email_msg.is_multipart():
        the_payload_complex = []
        for part_msg in email_msg.get_payload():
            the_payload_complex.append(serialize_email_message(part_msg))
    else:
        the_payload_primitive = email_msg.get_payload()
    headers = {}
    for header_key in email_msg.keys():
        headers[header_key] = _decode_encdoded_words_in_header_list(email_msg.get_all(header_key))
    curr_msg =  {
                'content' : the_payload_primitive,
                'child_messages' : the_payload_complex,
                'headers' : headers,
                }
    curr_msg['content_type'] = parse_content_types(curr_msg)
    return curr_msg

def serialize_email_raw_message(email_str):
    """
    Convert an email given as string to a serializable dictionary representation.
    """
    return serialize_email_message(email.message_from_string(email_str))

def serialize_email_with_context(email_context_dict):
    """
    This function awaits a dictionary as argument.
    That dictionary must contain the key 'raw_message' pointing to a RFC822 conform string.
    This document will be analyzed and the resulting reserialized data will be added to the dictionary.
    """
    raw_rfc822_msg = email_context_dict['raw_message']
    # hash:
    email_context_dict['hash'] = hashlib.sha256(raw_rfc822_msg).hexdigest()
    # message:
    serialized_msg = serialize_email_raw_message(raw_rfc822_msg)
    email_context_dict['message'] = serialized_msg
    # msg_id:
    email_context_dict['msg_id'] = _get_first_header_entry(serialized_msg, 'Message-ID')
    # references:
    msg_ref = set()
    for ref_keyword in ('References', 'In-Reply-To', 'X-Forwarded-Message-Id'):
        header_lines = _get_header_entries(serialized_msg, ref_keyword)
        if header_lines:
            for header_line in header_lines:
                msg_ref |= set(header_line.split())
    email_context_dict['references'] = list(msg_ref)
    return email_context_dict




