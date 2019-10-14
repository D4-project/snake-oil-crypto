#!/usr/bin/env sage -python
from . import register_attack
from . import Attack
from rq import Queue, Connection
from redis import Redis
from sage.all import *

@register_attack
class Ecma(Attack):
    def process(self, X):
        f = ECM()
        return(sorted(f.find_factor(X, None, 2000)))

    def report(self, processid):
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            print(res.return_value)
