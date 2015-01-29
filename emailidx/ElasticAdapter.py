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
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from emailidx.settings import Settings

_es = Elasticsearch(hosts=Settings.ES_HOSTS)
#########################################################################################
#                                      Generators                                       #
#########################################################################################
def _generate_email_data_for_bulk_index(to_add, to_delete):
    """
    Generates bulk commands to be used by save_email_data_to_db.
    """
    for email in to_add:
        msg_id = email['msg_id'] if email['msg_id'] else "[UNKNOWN]"
        print "[ES] Archiving %s ..." % msg_id
        yield {
                '_index' : Settings.ES_INDEX_EMAILS,
                '_type' : Settings.ES_TYPE_EMAIL,
                '_source' : email,
               }
    for entry_id in to_delete:
        print "[ES] Deleting %s ..." % entry_id
        yield {
                '_op_type':  'delete',
                '_index': Settings.ES_INDEX_EMAILS,
                '_type': Settings.ES_TYPE_EMAIL,
                '_id': entry_id
               }
#########################################################################################
#                                      Functions                                        #
#########################################################################################
def database_exists():
    """
    Returns if the database (index & type) exists.
    """
    return _es.indices.exists_type(index=Settings.ES_INDEX_EMAILS, doc_type=Settings.ES_TYPE_EMAIL)

def delete_database():
    """
    Deletes the database/index.
    Doesn't fail if the db doesn't exist.
    """
    if database_exists():
        _es.indices.delete(index=Settings.ES_INDEX_EMAILS)
        
def create_database():
    """
    Creates database index with a basic mapping
    """
    basic_fields_mapping = {
        'mappings': {
            Settings.ES_TYPE_EMAIL: {
                'properties': {
                    'hash': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    },
                    'mailbox': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    },
                    'msg_id': {
                        'type': 'string',
                        'index' : 'not_analyzed'
                    },
                    'references': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    }
                }
            }
        }
    }
    _es.indices.create(Settings.ES_INDEX_EMAILS, basic_fields_mapping)


def save_email_data_to_db(to_add, to_delete):
    """
    Adds/deletes database entries according to the given data.
    Database will be created on-the-fly.
    
    Keyword arguments:
    to_add -- list of serialized emails that will be added to the db
    to_delete -- list of the ids of emails that will be removed from the db
    """
    if not database_exists():
        create_database()
    stats = elasticsearch.helpers.bulk(_es, _generate_email_data_for_bulk_index(to_add, to_delete), stats_only=True)
    print "[ES] %i successful transactions" % stats[0]
    print "[ES] %i failed transactions" % stats[1]
    
def get_email_ids_sorted_by_mailbox():
    """
    Returns a dictionary containing the ids of all emails in the db sorted by mailbox and hash.
    """
    if database_exists():
        query_result = elasticsearch.helpers.scan(_es, index=Settings.ES_INDEX_EMAILS, doc_type=Settings.ES_TYPE_EMAIL, fields='hash,mailbox')
        mbx_hashlist = {}
        for hit in query_result:
            the_mbx = hit['fields']['mailbox'][0]
            the_hash = hit['fields']['hash'][0]
            the_id = hit['_id']
            if the_mbx not in mbx_hashlist:
                mbx_hashlist[the_mbx] = {}
            if the_hash not in mbx_hashlist[the_mbx]:
                mbx_hashlist[the_mbx][the_hash] = []
            mbx_hashlist[the_mbx][the_hash].append(the_id)
        return mbx_hashlist
    else:
        return {}
        

