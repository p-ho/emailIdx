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
import commentjson, os, imp, sys

# EXPOSED VARIABLES
content_filters = None
settings = None

ENV_SETTINGS_NAME = 'EIDX_SETTINGS_FILE'
CONTENT_FILTERS_BASE_PATH = os.path.join(os.path.dirname(__file__), 'contentfilter')
#########################################################################################
#                                ContentFilter Class                                    #
#########################################################################################
class ContentFilter:
    def __init__(self, id, module_name, settings=None):
        self.id = id
        self.module_name = module_name
        self.settings = settings if settings is not None else {}
        
    def __str__(self):
        return "<ContentFilter %s at module %s>" % (self.id, self.module_name)
    
    def __repr__(self):
        return self.__str__()
    
    def import_module(self):
        imp.acquire_lock()
        fp, pathname, description = imp.find_module(self.module_name, [CONTENT_FILTERS_BASE_PATH])
        try:
            return imp.load_module(self.module_name, fp, pathname, description)
        finally:
            imp.release_lock()
            if fp:
                fp.close()
#########################################################################################
#                                  Helper Functions                                     #
#########################################################################################
def _get_settings_file_path():
    # TODO: Add other ways to declare settings file
    env_settings_file = os.environ.get(ENV_SETTINGS_NAME)
    if env_settings_file:
        if os.path.exists(env_settings_file):
            return env_settings_file
        else:
            print >> sys.stderr, "[INI_ERR] The file '%s' doesn't exist." % env_settings_file
            return None
    else:
        print >> sys.stderr, "[INI_ERR] Declaring $%s is currently the only way specify the settings file. You can use the file 'sample_settings.json' as a settings template." % ENV_SETTINGS_NAME

def _require_paths_from_object(obj, paths):
    tempObj = None
    for path in paths:
        tempObj = obj
        for path_segment in path:
            if path_segment not in tempObj:
                return (False, path)
            tempObj = tempObj[path_segment]
    return (True, None)
            
def _prepare_contentfilters(cf_obj):
    global content_filters
    content_filters = []
    cf_list = cf_obj['order']
    cf_dict = cf_obj['filters']
    for cf_id in cf_list:
        content_filters.append(ContentFilter(cf_id, cf_dict[cf_id]['py_module'], cf_dict[cf_id].get('settings')))
    
#########################################################################################
#                                      Functions                                        #
#########################################################################################
def init_settings():
    global settings
    settings_file_path = _get_settings_file_path()
    if not settings_file_path:
        return False
    with open(settings_file_path) as settings_file:
        settings_obj = commentjson.load(settings_file)
        req_res, req_path =  _require_paths_from_object(settings_obj,
                                          [
                                           ("imap", "tls_method"),
                                           ("imap", "tls_verify_method"),
                                           ("imap", "use_cram_transfer"),
                                           ("imap", "port"),
                                           ("imap", "credentials", "host"),
                                           ("imap", "credentials", "user"),
                                           ("imap", "credentials", "password"),
                                           ("elasticsearch", "hosts"),
                                           ("elasticsearch", "type_email"),
                                           ("elasticsearch", "index_emails"),
                                           ("sync_behavior", "reset_db_before_sync"),
                                           ("sync_behavior", "sync_delete"),
                                           ("sync_behavior", "excluded_mailboxes"),
                                           ("sync_behavior", "keep_raw_messages"),
                                           ("contentfilters", "order"),
                                           ("contentfilters", "filters"),
                                           ("misc", "ssl_certs_dir")
                                           ])
        
        if not req_res:
            print >> sys.stderr, "[INI_ERR] The settings file is missing the property '%s'" % '.'.join(req_path)
            return False
        
        _prepare_contentfilters(settings_obj['contentfilters'])
        
        settings = {}
        for category in ('imap', 'elasticsearch', 'sync_behavior', 'misc'):
            settings[category] = settings_obj[category]
            
        return True


