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
#                                  Helper Functions                                     #
#########################################################################################
def _diff_equiv_lists(left_list, right_list):
    """
    Returns a tuple consisting of the given lists that where shortened by the difference of their lengthes.
    All items are assumed to be equivalent.
    """
    len_diff = len(right_list) - len(left_list)
    
    if len_diff == 0:
        return ([], [])
    elif len_diff > 0:
        return ([], right_list[:len_diff])
    else:
        return (left_list[:-len_diff], [])
#########################################################################################
#                                      Functions                                        #
#########################################################################################
def diff_single_mailbox(imap_mbx, es_mbx):
    """
    Returns a dictionary containing the difference of emails from IMAP and from ES in a single mailbox.
    """
    imap_overlap = []
    es_overlap = []
    hashes = set(imap_mbx.keys())
    hashes.update(set(es_mbx.keys()))
    
    for msg_hash in hashes:
        msg_list_imap = imap_mbx.get(msg_hash, [])
        msg_list_es = es_mbx.get(msg_hash, [])
        msg_list_diff = _diff_equiv_lists(msg_list_imap, msg_list_es)
        imap_overlap.extend(msg_list_diff[0])
        es_overlap.extend(msg_list_diff[1])
        
    return {
            'imap_overlap' : imap_overlap,
            'es_overlap' : es_overlap,
            }    
    

def diff_mailbox_structures(imap_tree, es_tree):
    """
    Returns a dictionary containing the difference of emails from IMAP and from ES.
    """
    imap_overlap = []
    es_overlap = []
    mbx_names = set(imap_tree.keys())
    mbx_names.update(set(es_tree.keys()))
    for mbx_name in mbx_names:
        mbx_imap = imap_tree.get(mbx_name, {})
        mbx_es = es_tree.get(mbx_name, {})
        overlaps = diff_single_mailbox(mbx_imap, mbx_es)
        imap_overlap.extend(overlaps['imap_overlap'])
        es_overlap.extend(overlaps['es_overlap'])
        
    return {
            'imap_overlap' : imap_overlap,
            'es_overlap' : es_overlap,
            } 


