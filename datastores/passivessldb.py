from . import register_datastore
from . import DataStore
import datetime
from datetime import date
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
class PassivesslDB(DataStore):
    def __init__(self):
        self.name = "default datastore: D4 passiveSSL sqlalchemy backend"
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
        """ Connect to the database server """
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = engine_from_config(self.params, prefix='sqlalchemy.')
            # self.conn = engine_from_config(self.params, prefix='sqlalchemy.', echo = True)
            self.meta = MetaData(self.conn)
            self.pkTable = Table('public_key', self.meta, autoload=True)
            self.certTable = Table('certificate', self.meta, autoload=True)
            self.pkcLink = Table('many_certificate_has_many_public_key', self.meta, autoload=True)
            self.sessionTable = Table('sessionRecord', self.meta, autoload=True)
            self.srcLink = Table('many_sessionRecord_has_many_certificate', self.meta, autoload=True)

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
        s = (select([self.pkTable.c.modulus]), select([self.pkTable.c.modulus]).distinct(self.pkTable.c.modulus))[distinct]

        try:
            s = s.where(self.pkTable.c.type == 'RSA')
            if maxSize > 0:
                s = s.where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus_size < maxSize / 8))
            s = (s.order_by(desc(self.pkTable.c.modulus)), s.order_by(asc(self.pkTable.c.modulus)))[order == 'asc']
            s = s.offset(off)
            if lim > 0:
                s = s.limit(lim)

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

        s = (select([self.pkTable.c.modulus]), select([self.pkTable.c.modulus]).distinct(self.pkTable.c.modulus))[distinct]
        s = s.select_from(join(self.pkTable, self.pkcLink, self.pkcLink.c.hash_public_key == self.pkTable.c.hash).join(self.certTable, self.certTable.c.hash == self.pkcLink.c.hash_certificate))

        try:
            s = s.where(and_(self.pkTable.c.type == 'RSA', self.certTable.c.subject.ilike("%{}%".format(subject))))
            if maxSize > 0:
                s = s.where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus_size < maxSize/8, self.certTable.c.subject.ilike("%{}%".format(subject))))
            s = (s.order_by(desc(self.pkTable.c.modulus)), s.order_by(asc(self.pkTable.c.modulus)))[order == 'asc']
            s = s.offset(off)
            if lim > 0:
                s = s.limit(lim)

            rows = self.conn.execute(s)
            l = []
            for r in rows:
                l.append(r['modulus'])
            result = [ZZ(i) for i in l]
            rows.close()
        except (Exception) as error:
            print(error)

        return result

    def getRSAModuliByIP(self, off=0, lim=0, maxSize = 0, order='desc', srcIP = None, dstIP = None, distinct = False):
        """ query RSA Public Keys' moduli between cursors for a an IP """
        # TODO use sqlalchemy, with psql dialect
        # s = (select([self.pkTable.c.modulus]), select([self.pkTable.c.modulus]).distinct(self.pkTable.c.modulus))[distinct]
        # s = s.select_from(
            # join(self.certTable, self.certTable.c.hash == self.srcLink.c.hash_certificate)
            # join(self.sessionTable, self.srcLink, self.srcLink.c.id_sessionRecord == self.sessionTable.c.id)
            # join(self.pkTable, self.pkcLink, self.pkcLink.c.hash_public_key == self.pkTable.c.hash)
            # .join(self.certTable, self.certTable.c.hash == self.pkcLink.c.hash_certificate)
        # )

        rawQuery = 'SELECT DISTINCT public_key.modulus ' \
           'FROM public_key ' \
           'JOIN many_certificate_has_many_public_key ON many_certificate_has_many_public_key.hash_public_key = public_key.hash ' \
           'JOIN certificate ON certificate.hash = many_certificate_has_many_public_key.hash_certificate ' \
           'JOIN public."many_sessionRecord_has_many_certificate" ON certificate.hash = public."many_sessionRecord_has_many_certificate".hash_certificate ' \
           'JOIN "sessionRecord" ON  "sessionRecord".id = "many_sessionRecord_has_many_certificate"."id_sessionRecord" '
# WHERE "sessionRecord"."dst_ip" = inet '60.243.245.99';

        try:

            if srcIP is not None and dstIP is not None:
                # TODO
                print("dst + src not implemented.")
                # s = s.where(and_(self.pkTable.c.type == 'RSA', self.sessionTable.c.src_ip.ilike("%{}%".format(srcIP)), self.sessionTable.c.dst_ip.ilike("%{}%".format(dstIP))))
            if srcIP is not None:
                target =  srcIP
                what =  '"src_ip"'
                # s = s.where(and_(self.pkTable.c.type == 'RSA', self.sessionTable.c.src_ip.ilike("%{}%".format(srcIP))))
            elif dstIP is not None:
                target =  dstIP
                what =  '"dst_ip"'
                # s = s.where(and_(self.pkTable.c.type == 'RSA', self.sessionTable.c.dst_ip.ilike("%{}%".format(dstIP))))

            rawQuery = '{} {}{} {} {};'.format(rawQuery, 'WHERE "sessionRecord".', what, '= inet', "'"+target+"'")

            # if maxSize > 0:
            #     s = s.where(and_(self.pkTable.c.type == 'RSA', self.pkTable.c.modulus_size < maxSize/8, self.certTable.c.subject.ilike("%{}%".format(subject))))
            # s = (s.order_by(desc(self.pkTable.c.modulus)), s.order_by(asc(self.pkTable.c.modulus)))[order == 'asc']
            # s = s.offset(off)
            # if lim > 0:
            #     s = s.limit(lim)

            # rows = self.conn.execute(s)
            rows = self.conn.execute(rawQuery)
            l = []
            for r in rows:
                l.append(r['modulus'])
            result = [ZZ(i) for i in l]
            rows.close()
        except (Exception) as error:
            print(error)

        return result

        return False


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
        set = update(self.pkTable).where(self.pkTable.c.modulus==str(match[0])).values(P=str(match[1]), misp=True)
        self.conn.execute(set)

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

    def getUnpublishedKeys(self, since = date.today()):
        """
        Returns keys that have not been published to MISP yet
        """
        s = select([self.pkTable.c.hash,
                    self.pkTable.c.modulus,
                    self.pkTable.c.modulus_size,
                    self.pkTable.c.P,
                    self.pkTable.c.Q,
                    self.pkTable.c.exponent,
                    self.pkTable.c.type,
                    ])
            # since timestamp, only support RSA ATM
        s = s.where(
            and_(
                self.pkTable.c.type == 'RSA',
                self.pkTable.c.P != None,
                or_(
                    self.pkTable.c.misp != True,
                    self.pkTable.c.misp == None),
                or_(
                    self.pkTable.c.published >= since,
                    self.pkTable.c.published == None),
                ))

        try:
            rows = self.conn.execute(s)
            res = rows.fetchall()
            rows.close()
        except (Exception) as error:
            print(error)

        return res

    def getCertificatesForKey(self, keyHash):
        """
        Returns certificates using a key as array of dictionary
        """
        s = select([
                    self.certTable.c.hash,
                    self.certTable.c.subject,
                    self.certTable.c.issuer
                    ])
        s = s.select_from(join(self.pkTable, self.pkcLink, self.pkcLink.c.hash_public_key == self.pkTable.c.hash).join(self.certTable, self.certTable.c.hash == self.pkcLink.c.hash_certificate))
        s = s.where(self.pkTable.c.hash == keyHash)

        try:
            rows = self.conn.execute(s)
            res = rows.fetchall()
            rows.close()
        except (Exception) as error:
            print(error)

        return res

    def setPublished(self, match):
        """ touch published date after publishing """
        set = update(self.pkTable).where(and_(self.pkTable.c.modulus==str(match[0]), self.pkTable.c.modulus==True)).values(published=datetime.datetime.now())
        self.conn.execute(set)

