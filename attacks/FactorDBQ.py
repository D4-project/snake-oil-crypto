#!/usr/bin/env sage -python
from . import register_attack
from . import Attack
from rq import Queue, Connection
from redis import Redis
from factordb.factordb import FactorDB
from sage.all import *

@register_attack
class FactorDBQ(Attack):
    def process(self, X):
        try:
            f = FactorDB(X)
            f.connect()
            if f.get_status() in ['FF', 'CF']:
                return int(f.get_factor_list()[0])
        except ImportError:
            return None

    def report(self, processid):
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            print(res.return_value)