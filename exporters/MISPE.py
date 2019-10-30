#!/usr/bin/env sage -python
from . import register_exporter
from . import Exporter
from rq import Queue, Connection
from redis import Redis
from sage.all import *
from pymisp import ExpandedPyMISP
from exporters.generator import FeedGenerator

@register_exporter
class MISPE(Exporter):

    def __init__(self, source):
        """" MISPE can push from an attack, or from a datastore that supports it """
        super().__init__()
        self.name = 'MISP exporter'
        self.source = source
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
        cm = {
            "text": "This is a test"
        }
        self.generator.add_object_to_event("crypto-material", **cm)

