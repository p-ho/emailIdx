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
import StringIO, base64, sys, getpass
from pdfminer.pdfdocument import PDFDocument, PDFPasswordIncorrect
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

pdfsettings = None
#########################################################################################
#                                   Helper Functions                                    #
#########################################################################################
def _build_toc_tree(outlines, startIdx=0):
    """
    Build 'table of contents' tree from pdfminer data.
    """
    if len(outlines) == 0:
        return None, -1
    
    toplevel_forest = []
    toplevel_rank = outlines[startIdx][0]
    
    i=startIdx
    while i < len(outlines):
        curr_rank = outlines[i][0]
        if curr_rank == toplevel_rank:
            toplevel_forest.append({ 'title' : outlines[i][1] })
            i += 1
        elif curr_rank < toplevel_rank:
            return toplevel_forest, i
        else:
            child_tree, i = _build_toc_tree(outlines, i)
            toplevel_forest[-1]['subsections'] = child_tree
            
    return toplevel_forest, i
#########################################################################################
#                                    Actual Parsing                                     #
#########################################################################################
def actual_parse_pdf(pdf_data):
    infp = StringIO.StringIO(buf=pdf_data)
    parser = PDFParser(infp)
    
    password = b''
    pw_accepted = False
    curr_pw_idx = 0
    while not pw_accepted:
        try:
            document = PDFDocument(parser, password=password)
            pw_accepted = True
            
        except PDFPasswordIncorrect, pwex:
            if len(pdfsettings['passwords']) > curr_pw_idx:
                password = pdfsettings['passwords'][curr_pw_idx]
                curr_pw_idx += 1
            elif pdfsettings['ask_password']:
                password = getpass.getpass("PDF password:")
                if password == '':
                    raise  pwex
            else:
                raise pwex
            
    # get table of contents
    outlines = [outline for outline in document.get_outlines()]
    toc = _build_toc_tree(outlines)[0]
        
    # get text contents
    outfp = StringIO.StringIO()
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, outfp, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        
    txt_contents = outfp.getvalue()
    
    infp.close()
    device.close()
    outfp.close()
    
    return {
            'txt_contents' : txt_contents,
            'table_of_contents' : toc,
            }
#########################################################################################
#                                   Exposed Functions                                   #
#########################################################################################
def is_pdf(message_part, filter_method):
    content_type = message_part['content_type']
    return content_type['_type'] == 'application/pdf'


def try_parse_pdf(message_part, filter_method):
    if 'Content-Transfer-Encoding' in message_part['headers']:
        ctenc = message_part['headers']['Content-Transfer-Encoding']
        if 'base64' in ctenc:
            pdf_data = base64.b64decode(message_part['content'])
            message_part['content_parsed'] = actual_parse_pdf(pdf_data)
        else:
            print >>sys.stderr, "[%s] %s encoding is not supported." % (filter_method, ctenc)
        
        
def __get_content_filter_functions__(settings):
    global pdfsettings
    pdfsettings = settings
    return (is_pdf, try_parse_pdf)

