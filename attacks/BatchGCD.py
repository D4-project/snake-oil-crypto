#!/usr/bin/env sage -python
from . import register_attack
from . import Attack
import datastores
from rq import Queue, Connection
from redis import Redis
from sage.all import *
import hashlib

@register_attack
class BatchGCD(Attack):

    def __init__(self, datastore):
        self.name = 'BatchGCD attack'
        self.ds = datastore

    def process(self, args, kwargs=None):
        """ process invoques args, a datastore function, with kwargs as its arguments,
         then proceed with performing the attack on the results """
        m = hashlib.sha256()
        with self.ds:
            X = args() if kwargs is None else args(**kwargs)
            # Added a hash to easily compare inputs between batches
            m.update(str(X).encode('UTF-8'))
            print("\033[92m"+"Attacking {0} keys - {1}.".format(len(X), m.hexdigest())+"\033[0m")
            return [X, self.batchgcd_faster(X)]

    def report(self, processid):
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            # TODO investigate coprimes, what is the effec of sharing p AND q
            match = [x for x in zip(res.return_value[0], res.return_value[1]) if x[1] != 1 and x[0] != x[1]]
            # match = [x for x in zip(res.return_value[0], res.return_value[1]) if x[1] != 1]
            #  TODO move this code to an export to csv file method
            # if len(match) > 1:
            #     with open('output_text2/'+processid, 'w+') as rf:
            #         for line in match:
            #             rf.write("{0},{1}\n".format(line[0], line[1]))
            print("\033[93m Factorized keys: {0} out of {1} \033[0m".format(len(match), format(len(res.return_value[0]))))
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