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
from bs4 import BeautifulSoup
#########################################################################################
#                                   Exposed Functions                                   #
#########################################################################################
#
# This Content Filter must be run AFTER PlainTextDecoder
#
def try_extract_text_from_html(message_part, filter_method):
    soup = BeautifulSoup(message_part['content_parsed']['txt_contents'])
    for script in soup(['script', 'style']):
        script.extract()
    extracted_text = soup.get_text()
    
    lines = (line.strip() for line in extracted_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    extracted_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    message_part['content_parsed']['html_contents'] = message_part['content_parsed']['txt_contents']
    message_part['content_parsed']['txt_contents'] = extracted_text

def is_html(message_part, filter_method):
    return message_part['content_type']['_type'] == 'text/html' \
        and 'content_parsed' in message_part \
        and 'txt_contents' in message_part['content_parsed']

def __get_content_filter_functions__():
    return (is_html, try_extract_text_from_html)
