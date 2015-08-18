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
import StringIO, base64, sys
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.table import Table
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
#########################################################################################
#                                    Actual Parsing                                     #
#########################################################################################
def _get_docx_part_as_text(doc_part):
    """
    Get all text components from the given BlockItemContainer.
    """
    res_text = ""
    for ele in doc_part._element:
        if isinstance(ele, CT_Tbl):
            tbl = Table(ele, doc_part)
            for row in tbl.rows:
                for cell in row.cells:
                    res_text += _get_docx_part_as_text(cell) + "\n"
        elif isinstance(ele, CT_P):
            res_text += Paragraph(ele, doc_part).text + "\n"
    return res_text

def get_docx_as_text(docx_data):
    """
    Get all text components from the given DocX data.
    """
    in_stream = StringIO.StringIO(buf=docx_data)
    document = Document(in_stream)
    root_doc_part = document._body
    docx_as_text = _get_docx_part_as_text(root_doc_part)
    in_stream.close()
    return docx_as_text

def actual_parse_docx(docx_data):
    return { 'txt_contents' : get_docx_as_text(docx_data) }
#########################################################################################
#                                   Exposed Functions                                   #
#########################################################################################
def is_docx(message_part, filter_method):
    content_type = message_part['content_type']
    return content_type['_type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

def try_parse_docx(message_part, filter_method):
    if 'Content-Transfer-Encoding' in message_part['headers']:
        ctenc = message_part['headers']['Content-Transfer-Encoding']
        if 'base64' in ctenc:
            docx_data = base64.b64decode(message_part['content'])
            message_part['content_parsed'] = actual_parse_docx(docx_data)
        else:
            print >>sys.stderr, "[%s] %s encoding is not supported." % (filter_method, ctenc)
        
def __get_content_filter_functions__(settings):
    return (is_docx, try_parse_docx)
