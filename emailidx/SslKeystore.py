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
import os, sys, errno
from M2Crypto import X509, EVP
from emailidx.settings import Settings
#########################################################################################
#                                 Global Variables                                      #
#########################################################################################
CERT_EXT = '.pem'
KEY_EXT = '.key'

"""The actual keystore"""
keystore = []
#########################################################################################
#                                      Functions                                        #
#########################################################################################
def add_keys_to_store(key, cert, email):
    """
    Loads the given key pair objects to keystore.
    
    Keyword arguments:
    key -- M2Crypto key object
    cert_file -- M2Crypto certificate object
    email -- corresponding email address
    """
    keystore.append({ 'key' : key, 'cert' : cert, 'email' : email })


def load_keys_from_files(key_file, cert_file):
    """
    Loads the given key pair files to keystore.
    
    Keyword arguments:
    key_file -- path of key file
    cert_file -- path of certificate file
    """
    the_cert = X509.load_cert(cert_file)
    the_key = EVP.load_key(key_file)
    email_list = the_cert.get_subject().get_entries_by_nid(X509.X509_Name.nid['Email'])
    email = str(email_list[0].get_data()) if len(email_list) > 0 else None
    add_keys_to_store(the_key, the_cert, email)
        

def load_keys_from_directory(directory):
    """
    Loads S/MIME keys from the given directory to the in-memory keystore.
    (The keyfiles must be named *.pem for public certificate and *.key for private key)
    """
    if not os.path.isdir(directory):
        print >> sys.stderr, "[KEYSTORE] Can't load the directory '%s' to read SSL keys." % directory
        sys.exit(errno.ENOENT)
    for filename in os.listdir(directory):
        filename = os.path.basename(filename)
        name, ext = os.path.splitext(filename)
        if ext.lower() == CERT_EXT:
            files_path = os.path.join(directory, name)
            load_keys_from_files(files_path + KEY_EXT, files_path + CERT_EXT)
            
            
def fill_keystore():
    """
    Loads S/MIME keys from the directory specified by settings to the in-memory keystore.
    (The keyfiles must be named *.pem for public certificate and *.key for private key)
    """
    if Settings.SSL_CERTS_DIR is not None:
        load_keys_from_directory(Settings.SSL_CERTS_DIR)

        


