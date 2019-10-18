from . import register_datastore
from . import DataStore
from sqlalchemy import engine_from_config
from sqlalchemy import select
from sqlalchemy import join
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.sql import and_, or_, not_, desc, asc
from sqlalchemy import update
from configparser import ConfigParser
from rq import Queue, Connection
from redis import Redis
from sage.all import *
import pdb


@register_datastore
class PostGres(DataStore):
    def __init__(self):
        self.name = "default datastore: D4 passiveSSL PSQL backend"
        # read connection parameters
        self.params = self.config()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self ,exc_type, exc_value, tb):
        self.disconnect()
        if exc_type is not None:
            return False
        return True

    def config(self, filename='config.conf', section='sqlalchemy'):
        parser = ConfigParser()
        parser.read(filename)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return db

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = engine_from_config(self.params, prefix='sqlalchemy.')
            self.meta = MetaData(self.conn)
            self.pkTable = Table('public_key', self.meta, autoload=True)
            self.certTable = Table('certificate', self.meta, autoload=True)
            self.pkcLink = Table('many_certificate_has_many_public_key', self.meta, autoload=True)

        except (Exception) as error:
            print(error)

    def disconnect(self):
        if self.conn is not None:
            self.conn.dispose()
            self.conn = None
        print('Database connection closed.')

    def getRSA(self, off=0, lim=0):
        """ query Public Keys between cursors """
        try:
            s = self.pkTable.select(offset = off, limit = lim)
            rows = self.conn.execute(s)
        except (Exception) as error:
            print(error)
        return rows

    def getRSAModuli(self, off=0, lim=0, order='desc', maxSize = 0, distinct = False):
        """ query RSA Public Keys' moduli between cursors """

        if (off == 0) and (lim == 0):
            s = select([self.pkTable.c.modulus])
        else:
            s = select([self.pkTable.c.modulus], offset = off, limit = lim)

        try:
            s = s.where(self.pkTable.c.type == 'RSA')
            if maxSize > 0:
                s = s.where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus_size < maxSize / 8))

            s = (s.order_by(desc(self.pkTable.c.modulus)), s.order_by(asc(self.pkTable.c.modulus)))[order == 'asc']
            s = (s, s.distinct(self.pkTable.c.modulus))[distinct]
            rows = self.conn.execute(s)
            l = []
            for r in rows:
                l.append(r['modulus'])
            result = [ZZ(i) for i in l]
            rows.close()
        except (Exception) as error:
            print(error)

        return result

    def getRSAModuliBySubject(self, off=0, lim=0, maxSize = 0, order='desc', subject = None, distinct = False):
        """ query RSA Public Keys' moduli between cursors for a subject """

        if (off == 0) and (lim == 0):
            s = select([self.pkTable.c.modulus])
        else:
            s = select([self.pkTable.c.modulus], offset = off, limit = lim)

        s = s.select_from(join(self.pkTable, self.pkcLink, self.pkcLink.c.hash_public_key == self.pkTable.c.hash).join(self.certTable, self.certTable.c.hash == self.pkcLink.c.hash_certificate))

        try:
            s = s.where(and_(self.pkTable.c.type == 'RSA', self.certTable.c.subject.contains(subject)))
            if maxSize > 0:
                s = s.where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus_size < maxSize/8, self.certTable.c.subject.contains(subject)))
            s = (s.order_by(desc(self.pkTable.c.modulus)), s.order_by(asc(self.pkTable.c.modulus)))[order == 'asc']
            s = (s, s.distinct(self.pkTable.c.modulus))[distinct]
            rows = self.conn.execute(s)
            l = []
            for r in rows:
                l.append(r['modulus'])
            result = [ZZ(i) for i in l]
            rows.close()
        except (Exception) as error:
            print(error)

        return result

    def getRSAModulus(self, hash):
        """ query an RSA Public Keys' modulus from its hash """
        try:
            s = select([self.pkTable.c.modulus]).where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.hash == hash))
            rows = self.conn.execute(s)
            result = ZZ(rows.fetchone()[0])
            rows.close()
            return result
        except (Exception) as error:
            print(error)

    def getRSAHash(self, modulus):
        """ query an RSA hash from its modulus """
        try:
            s = select([self.pkTable.c.hash]).where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus == modulus))
            rows = self.conn.execute(s)
            result = ZZ(rows.fetchone()[0])
            rows.close()
            return result
        except (Exception) as error:
            print(error)

    def getRSAHashes(self, moduli):
        """ query an array of tuple RSA, hash from a list of moduli """
        try:
            s = select([self.pkTable.c.hash]).where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus == modulus))
            rows = self.conn.execute(s)
            result = ZZ(rows.fetchone()[0])
            rows.close()
            return result
        except (Exception) as error:
            print(error)


    def setRSAPrime(self, match):
        """ set a prime number once recovered """
        up = update(self.pkTable).where(self.pkTable.c.modulus==str(match[0])).values(P=str(match[1]))
        self.conn.execute(up)

    def pushResults(self, processid):
        """ push computation results into the datastore """
        with Connection(Redis()):
            q = Queue()
            res = q.fetch_job(processid)
            if res.return_value != None:
                self.connect()
                for match in res.return_value:
                    try:
                        self.setRSAPrime(match)
                    except (Exception) as error:
                        print(error)
                return true
            else:
                return false


