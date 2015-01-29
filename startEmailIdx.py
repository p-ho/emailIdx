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
#                       _ _ _____    _        #
#                      (_) |_   _|  | |       #
#   ___ _ __ ___   __ _ _| | | |  __| |_  __  #
#  / _ \ '_ ` _ \ / _` | | | | | / _` \ \/ /  #
# |  __/ | | | | | (_| | | |_| || (_| |>  <   #
#  \___|_| |_| |_|\__,_|_|_|_____\__,_/_/\_\  #
#                                             #
#  --- USE THIS SCRIPT FOR TESTING ONLY ---   #
###############################################
import sys
from emailidx import Emailidx

if __name__ == '__main__':
    sys.exit(Emailidx.main())
    