#!/usr/bin/env sage -python
from . import register_exporter
from . import Exporter
from rq import Queue, Connection
from redis import Redis
from sage.all import *
from pymisp import ExpandedPyMISP
from exporters.generator import FeedGenerator
import pdb

@register_exporter
class MISPE(Exporter):

    def __init__(self, source):
        """" MISPE exports borked keys to MISP along with
        the certificates that use these keys, and the TLS session
        in which they appear. 
        :type source: an attack, or a datastore"""
        
        super().__init__()
        self.name = 'MISP exporter'
        self.url = self.config['CREDENTIALS']['URL']
        self.key = self.config['CREDENTIALS']['KEY']
        self.misp = ExpandedPyMISP(self.url, self.key, False)
        tags = [
            {
                "colour": "#ffffff",
                "name": "tlp:white"
            },
            {
                "colour": "#ff00ff",
                "name": "d4-crypto-feed"
            }
        ]
        self.generator = FeedGenerator(self.config, tags)
        self.misp.toggle_global_pythonify()
        #  Depending on the type of source
        self.source = source
        process = self.switcher(str(type(self.source)).split("."))
        process()

    def switcher(self, sclass):
        parent = sclass[0][8:]
        if parent == 'attacks':
            return self.processAttack()
        child = sclass[1]
        print(child)
        switch = {
        'passivessldb' : self.processPassiveSSL,
        'textfile' : self.processFile
        }
        return switch.get(child)

    def processPassiveSSL(self):
        """
        Fecth latest cracked keys from passiveSSL DB and export these to the MISP instance
        """
        with self.source:
            ls = self.source.getUnpublishedKeys()
            for row in ls:
                cm = {
                    'p': str(row['P']),
                    'q': str(row['Q']),
                    'rsa-modulus-size': str(row['modulus_size']*8),
                    # Exponent in lacking for the misp object
                    # 'exponent': row['exponent'],
                    # private is lacking from DB
                    # 'private': row['private'],
                    'type': row['type'],
                }
                k_uuid = self.generator.add_object_to_event("crypto-material", **cm)
                print(k_uuid)
                certs = self.source.getCertificatesForKey(row['hash'])
                for cert in certs:
                    x509cert = {
                        'x509-fingerprint-sha1': str(cert['hash'])[2:-1],
                        'subject': cert['subject'],
                        'issuer': cert['issuer'],
                    }
                    relationship = {}
                    relationship['uuid'] = k_uuid
                    relationship['type'] = 'uses'
                    c_uuid = self.generator.add_object_to_event("x509", relationship, **x509cert)
                    print(c_uuid)
                    # Create the relationship

        self.generator.update_daily_event_id()
        self.generator.flush_event()

    def processFile(self):
        print("Export textfile results")

    def processAttack(self):
        print("Export attack results")



# self.source.name > batchGCD attack
