#!/usr/bin/env sage -python
from . import register_attack
from . import Attack
import datastores
from rq import Queue, Connection
from redis import Redis
from sage.all import *
import hashlib

@register_attack
class SearchGCD(Attack):

    def __init__(self, datastore, modulus):
        self.name = 'SearchGCD attack - search of a great common denominator on insertion'
        self.modulus = modulus
        self.ds = datastore

    def process(self, args, kwargs=None):
        """ process invoques args, a datastore function, with kwargs as its arguments,
         then proceed with performing the attack on the results. For correct results,
         BatchGCD attacks should be fed deduplicated slices """
        m = hashlib.sha256()
        with self.ds:
            X = args() if kwargs is None else args(**kwargs)
            # Added a hash to easily compare inputs between batches
            m.update(str(X).encode('UTF-8'))
            print("\033[92mAttacking {0} keys - {1}.\nwith\n{2}\033[0m".format(len(X), m.hexdigest(), self.modulus))
            for m in X:
                if m != self.modulus:
                    test = gcd(m, self.modulus)
                    if test != 1:
                        return [True, self.modulus, test]
            return [False, self.modulus]

    def report(self, processid):
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            if res.return_value[0] == False:
                print("\033[92m{0}\nhas no known common divisor in DB. \033[0m".format(res.return_value[1]))
                return True
            print("\033[31m{0}\nis common divisor of \n{1}. \033[0m".format(res.return_value[2], res.return_value[1]))
            return False
