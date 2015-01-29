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
#                             Imports & Global variables                                #
#########################################################################################
from emailidx.settings import InstalledContentFilters
import sys
#########################################################################################
#                                  Helper Functions                                     #
#########################################################################################
def _try_filter_content(message_part, id_to_display, filter_description):
    """
    Applies given content filter on the message part
    """
    (filter_method, content_filter) = filter_description
    try:
        filter_method_funcs = content_filter.__get_content_filter_functions__()
        if filter_method_funcs[0](message_part, filter_method):
            filter_method_funcs[1](message_part, filter_method)
    except:
        print >>sys.stderr, "[%s] Error with message %s" % (filter_method, id_to_display)
    

def _apply_content_filters_on_message_part(message_part, id_to_display, filter_description):
    """
    Applies given content filter on a part of a message recursively
    """
    _try_filter_content(message_part, id_to_display, filter_description)
    if ('message_decrypted' in message_part) and (message_part['message_decrypted'] is not None):
        _apply_content_filters_on_message_part(message_part['message_decrypted'], id_to_display, filter_description)
    if message_part['child_messages'] is not None:
        for child_msg in message_part['child_messages']:
            _apply_content_filters_on_message_part(child_msg, id_to_display, filter_description)
#########################################################################################
#                                      Functions                                        #
#########################################################################################
def apply_content_filters_on_email(email):
    """
    Applies all 'installed content filters' on the given serializable email message.
    """
    for filter_description in InstalledContentFilters.FILTER_METHODS:  
        id_to_display = email['msg_id'] if email['msg_id'] is not None else "Unknown"
        print "[%s] Filtering %s..." % (filter_description[0], id_to_display)
        _apply_content_filters_on_message_part(email['message'], id_to_display, filter_description)


def apply_content_filters_on_email_data(email_data):
    """
    Applies all 'installed content filters' on the given list of serializable email messages.
    """
    for msg in email_data:
        apply_content_filters_on_email(msg)

 

