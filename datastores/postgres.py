from . import register_datastore
from . import DataStore
from sqlalchemy import engine_from_config
from sqlalchemy import select
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.sql import and_, or_, not_
from configparser import ConfigParser
from sage.all import *


@register_datastore
class PostGres(DataStore):
    def __init__(self):
        self.name = "default datastore: D4 passiveSSL PSQL backend"
        self.connect()

    def config(self, filename='config.conf', section='sqlalchemy'):
        parser = ConfigParser()
        # read config file
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
        self.conn = None
        try:
            # read connection parameters
            params = self.config()
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = engine_from_config(params, prefix='sqlalchemy.')
            self.meta = MetaData(self.conn)
            self.pkTable = Table('public_key', self.meta, autoload=True)
          
        except (Exception) as error:
            print(error)

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()
        print('Database connection closed.')

    def getRSA(self, off=0, lim=0):
        """ query Public Keys between cursors """
        try:
            s = self.pkTable.select(offset = off, limit = lim)
            rows = self.conn.execute(s)
        except (Exception) as error:
            print(error)

        return rows

    def getRSAModuli(self, off=0, lim=0):
        """ query RSA Public Keys' moduli between cursors """
        try:
            if (off == 0) and (lim == 0):
                s = select([self.pkTable.c.modulus]).where(self.pkTable.c.type == 'RSA')
            else:
                s = select([self.pkTable.c.modulus], offset = off, limit = lim).where(self.pkTable.c.type == 'RSA')
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
        except (Exception) as error:
            print(error)

        return result