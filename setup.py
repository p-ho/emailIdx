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
###############################################
#                    Setup                    #
###############################################
#                       _ _ _____    _        #
#                      (_) |_   _|  | |       #
#   ___ _ __ ___   __ _ _| | | |  __| |_  __  #
#  / _ \ '_ ` _ \ / _` | | | | | / _` \ \/ /  #
# |  __/ | | | | | (_| | | |_| || (_| |>  <   #
#  \___|_| |_| |_|\__,_|_|_|_____\__,_/_/\_\  #
#                                             #
#                                             #
###############################################
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name='emailidx',
    version='0.2.0',

    description='Synchronizes emails from IMAP to Elasticsearch',
    author='Paul Hofmann',
    author_email='p.h.o@web.de',
    license='GPLv3',

    classifiers=[
        'Development Status :: 4 - Beta',
        
        'Environment :: Console',
        
        'Natural Language :: English',
        
        'Operating System :: OS Independent',
        
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        
        'Topic :: Communications :: Email :: Post-Office :: IMAP',
        'Topic :: Database',
        'Topic :: System :: Archiving',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(),

    install_requires=['elasticsearch', 'imaplib2', 'M2Crypto', 'python-gnupg', 'beautifulsoup4', 'pdfminer', 'python-docx', 'commentjson'],
    
    entry_points={
        'console_scripts': [
            'emailidx=emailidx.Emailidx:main',
        ],
    },
)
