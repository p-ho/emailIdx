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
#                                   IMAP Settings                                       #
#########################################################################################
# Used TLS method for IMAP connection
# - possible values: 'PLAIN', 'SSL/TLS' or 'STARTTLS'
IMAP_TLS_METHOD = 'STARTTLS'
# Method used to verify authenticity of the peer certificate
# - You may refer to CertificateVerifier.CERTIFICATE_VERIFY_METHOD for possible values
IMAP_TLS_VERIFY_METHOD = 'CHECK_CNAME_ONLY'
# Use CRAM-MD5 for password transfer
IMAP_USE_CRAM_MD5 = False
# IMAP port (None: Use default port)
IMAP_PORT = None
# IMAP credentials
IMAP_HOST = 'localhost'
IMAP_USER = 'the_user'
IMAP_PW = 'the_pw'
#########################################################################################
#                              ElasticSearch Settings                                   #
#########################################################################################
# Elasticsearch cluster description
# - cf. https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch
ES_HOSTS = [
            {'host': 'localhost', 'port' : 9200},
            ]
# type and index to use for the DB
# - There's no need to change them
ES_TYPE_EMAIL = 'email'
ES_INDEX_EMAILS = 'emails'
#########################################################################################
#                                   GPG Settings                                        #
#########################################################################################
# GPG home directory (None: Use default directory)
GPG_HOME = None
#########################################################################################
#                                 S/MIME Settings                                       #
#########################################################################################
# Path to the S/MIME certificates (None: Don't use S/MIME certs)
# - Public certificates must be provided as <name>.pem
# - Private keys must be provided as <name>.key
# - Where <name> must equal for corresponding key and certificate
SSL_CERTS_DIR = None
#########################################################################################
#                                  PDF Settings                                         #
#########################################################################################
# Ask interactively for PDF decryption
PDF_ASK_PASSWORD = False
# Predefined list of passwords to try for PDF decryption
PDF_PASSWORDS = ['exa', 'mple']
#########################################################################################
#                                  Sync Behavior                                        #
#########################################################################################
# Reset entire index before each sync
# - You shouldn't set it to True permanently
RESET_DB_BEFORE_SYNC = False
# Delete emails in DB as they are deleted in IMAP
SYNC_DELETE = True
# Exclude mailboxes from sync
SYNC_EXCLUDED_MAILBOXES = ['Trash']
# Copy raw RFC822 message to Elasticsearch
SYNC_KEEP_RAW_MESSAGE = False

