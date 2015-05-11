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
import sys
# emailidx imports are performed "on-the-fly"
#########################################################################################
#                                   Main Function                                       #
#########################################################################################
def main():
    """
    That's the main entrance point.
    """
    print """\
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
                                             
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.
For details refer to the GNU General Public License, version 3.
<http://opensource.org/licenses/GPL-3.0>
"""

    from emailidx import Settings
    print "[EIDX] Loading settings..."
    if not Settings.init_settings():
        print >> sys.stderr, "[INI_ERR] ERROR while reading settings."
        sys.exit(1)
    
    from emailidx import SslKeystore
    print "[EIDX] Loading S/MIME keys..."
    SslKeystore.fill_keystore()
    
    from emailidx import ImapAdapter
    print "[EIDX] Fetching emails..."
    email_tree_imap = ImapAdapter.fetch_all_emails_via_imap()
    
    from emailidx import ElasticAdapter
    if Settings.settings['sync_behavior']['reset_db_before_sync']:
        email_tree_es = {}
    else:
        print "[EIDX] Fetching DB data..."
        email_tree_es = ElasticAdapter.get_email_ids_sorted_by_mailbox()
        
    from emailidx import DiffMails
    print "[EIDX] Calculating diff..."
    diff_overlaps = DiffMails.diff_mailbox_structures(email_tree_imap, email_tree_es)
    emails_to_add = diff_overlaps['imap_overlap']
    print "[EIDX] emails to add:    %i" % len(emails_to_add)
    
    if Settings.settings['sync_behavior']['sync_delete']:
        emails_to_delete = diff_overlaps['es_overlap']
    else:
        emails_to_delete = []
        
    nmb_to_delete = 'ANY' if Settings.settings['sync_behavior']['reset_db_before_sync'] else str(len(emails_to_delete))
    print "[EIDX] emails to remove: %s" % nmb_to_delete
        
    from emailidx import ContentFilter
    print "[EIDX] Applying content filters..."
    ContentFilter.apply_content_filters_on_email_data(emails_to_add)
    
    if Settings.settings['sync_behavior']['reset_db_before_sync']:
        print "[EIDX] Resetting DB..."
        ElasticAdapter.delete_database()
        
    print "[EIDX] Writing to DB..."
    ElasticAdapter.save_email_data_to_db(to_add=emails_to_add, to_delete=emails_to_delete)
    
    print "[EIDX] DONE."
    
