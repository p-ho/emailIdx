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
from emailidx.contentfilter import SMimeDecryption, PgpDecryption, PdfParsing, DocxParsing, PlainTextDecoder, HTMLParsing
#########################################################################################
#                           List of installed content filters                           #
#########################################################################################
# The order of declaration may matter.
FILTER_METHODS = [
                  ('S/MIME', SMimeDecryption),
                  ('PGP/MIME', PgpDecryption),
                  ('PLAIN_TXT', PlainTextDecoder),
                  ('HTML', HTMLParsing),
                  ('PDF', PdfParsing),
                  ('DOCX', DocxParsing),
                  ]
