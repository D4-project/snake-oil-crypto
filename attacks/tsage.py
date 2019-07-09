#!/usr/bin/env sage-python
from . import register_attack
from . import Attack
from sage.all import *


@register_attack
class Tsage(Attack):
    def process(self, X):
        return self.batchgcd_faster(X)

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
