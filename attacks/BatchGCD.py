#!/usr/bin/env sage -python
from . import register_attack
from . import Attack
import datastores
from rq import Queue, Connection
from redis import Redis
from sage.all import *
import pdb

@register_attack
class BatchGCD(Attack):

    def __init__(self, datastore):
        self.name = 'BatchGCD attack'
        self.ds = datastore

    def process(self, args, kwargs=None):
        """ process invoques args, a datastore function, with kwargs as its arguments,
         then proceed with performing the attack on the results """
        with self.ds:
            X = args() if kwargs is None else args(**kwargs)
            return [X, self.batchgcd_faster(X)]

    def report(self, processid):
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            # TODO investigate coprimes
            match = [x for x in zip(res.return_value[0], res.return_value[1]) if x[1] != 1 and x[0] != x[1]]
            # print("From Reporting")
            print(match)
            print("Matching keys in TextFile: {0}".format(len(match)))
            return match

    def batchgcd_faster(self, X):
        prods = self.producttree(X)
        R = prods.pop()
        while prods:
            X = prods.pop()
            R = [R[floor(i // 2)] % X[i] ** 2 for i in range(len(X))]
        return [gcd(r // n, n) for r, n in zip(R, X)]

    def producttree(self, X):
        result = [X]
        while len(X) > 1:
            X = [prod(X[i * 2:(i + 1) * 2]) for i in range((len(X) + 1) // 2)]
            result.append(X)
        return result

    def remaindersusingproducttree(self, n, T):
        result = [n]
        for t in reversed(T):
            result = [result[floor(i // 2)] % t[i] for i in range(len(t))]
        return result

    def remainders(self, n, X):
        return self.remaindersusingproducttree(n, self.producttree(X))