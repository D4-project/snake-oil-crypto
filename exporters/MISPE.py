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
        """" MISPE can push from an attack, or from a datastore that supports it """
        super().__init__()
        self.name = 'MISP exporter'
        self.source = source
        pdb.set_trace()
        self.url = self.config['CREDENTIALS']['URL']
        self.key = self.config['CREDENTIALS']['KEY']
        self.misp = ExpandedPyMISP(self.url, self.key, False)
        self.misp.toggle_global_pythonify()
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
        cm = {
            "p": "1123451234512345123451234512345123451234512345123452345"
        }
        self.generator.add_object_to_event("crypto-material", **cm)
        self.generator.update_daily_event_id()
        self.generator.flush_event()

# self.source.name > batchGCD attack
