#!/usr/bin/env sage -python
from . import register_builder
from . import Builder
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from rq import Queue, Connection
from redis import Redis
from sage.all import *
import pdb

@register_builder
class RSABuilder(Builder):

    def __init__(self, **kwargs):
        super().__init__()
        self.h = None
        self.n = None
        self.e = None
        self.p = None
        self.q = None
        self.d = None
        self.name = 'RSA private key builder'
        self.folder = self.config['OUTPUT']['FOLDER']
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self, processid):
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            if res.return_value['success']:
                self._build(**res.return_value)
            else:
                return False

    def _build(self, **kwargs):
        """ process builds an RSa private from the given kargs """
        for key, value in kwargs.items():
            setattr(self, key, value)
        # print("{} {} {} {} {}".format(self.e, self.p, self.q, self.n, self.d))
        if self.e is not None and self.n is not None:
            if self.p is not None and self.q is not None:
                self._fromPandQ()
            else:
                if self.p is not None or self.q is not None:
                    self._fromP()
            if 'd' in kwargs and kwargs['d'] is not None:
                self.d = kwargs['d']
                self._fromD()
        else:
            print("Public Exponent, or modulus missing.")
            return False
        self._writeKeyToFile()

    def _fromP(self):
        if self.p is not None:
            self.q = int(self.n // self.p)
        else:
            self.p = int(self.n // self.q)
        self._fromPandQ()

    def _fromPandQ(self):
        self.phi_n = (self.p-1)*(self.q-1)
        self.d = inverse_mod(self.e, self.phi_n)
        dmp1 = rsa.rsa_crt_dmp1(self.d, self.p)
        dmq1 = rsa.rsa_crt_dmq1(self.d, self.q)
        iqmp = rsa.rsa_crt_iqmp(self.p, self.q)
        pn = rsa.RSAPublicNumbers(int(self.e), int(self.n))
        compositen = rsa.RSAPrivateNumbers(int(self.p), int(self.q), int(self.d), int(dmp1), int(dmq1), int(iqmp), pn)
        compositek = compositen.private_key(backend=default_backend())
        self.pem = compositek.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
                )

    # def _fromD(self):

    def _writeKeyToFile(self):
        path = self.folder+self.h+".pem"
        print("Writing key to file {}".format(path))
        f = open(path, "wb+")
        f.write(self.pem)
        f.close()
        print("Done.")
