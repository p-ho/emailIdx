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
from M2Crypto.SSL.Checker import Checker, WrongHost
#########################################################################################
#                                    Exceptions                                         #
#########################################################################################
class InsecureCertificateError(Exception):
    pass
#########################################################################################
#                                Verifier Functions                                     #
#########################################################################################
def verify_accept_any(certificate, host):
    print >>sys.stderr, "[IMAP_TLS] Insecure setting: ACCEPTING ANY CERTIFICATE"
    
def verify_deny_all(certificate, host):
    print >>sys.stderr, "[IMAP_TLS] Pointless setting: ACCEPTING NO CERTIFICATES AT ALL"
    raise InsecureCertificateError("DENY_ALL : No certificate is accepted")

def verify_check_cname_only(certificate, host):
    checker = Checker()
    try:
        checker(certificate, host)
    except WrongHost, wrong_host:
        raise InsecureCertificateError(wrong_host) 
    
def verify_check_ca_chain(certificate, host):
    # TODO: Not yet implemented.
    # - cf. https://fedorahosted.org/pulp/wiki/CertChainVerification
    raise NotImplementedError()
    
CERTIFICATE_VERIFY_METHOD = {
                             'ACCEPT_ANY': verify_accept_any,
                             'DENY_ALL': verify_deny_all,
                             'CHECK_CNAME_ONLY': verify_check_cname_only,
                             }

