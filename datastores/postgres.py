from . import register_datastore
from . import DataStore
from configparser import ConfigParser
import psycopg2
import numpy as np
from sage.all import *


@register_datastore
class PostGres(DataStore):
    def __init__(self):
        self.name = "default datastore: D4 passiveSSL PSQL backend"
        self.connect()

    def config(self, filename='config.conf', section='postgresql'):
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
        conn = None
        try:
            # read connection parameters
            params = self.config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)

            # create a cursor
            cur = conn.cursor()

            # execute a statement
            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version)

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def getRSA(self, offset=0, lim=0):
        """ query Public Keys between cursors """
        conn = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            with conn:
                with conn.cursor() as cur:

                    if (offset > 0) and (lim > 0):
                        cur.execute('SELECT modulus FROM "public"."public_key" '
                                    'WHERE "type" = \'RSA\' '
                                    'OFFSET %s '
                                    'LIMIT %s ', (offset, lim,))
                    elif offset > 0:
                        cur.execute('SELECT modulus FROM "public"."public_key" '
                                    'WHERE "type" = \'RSA\' '
                                    'OFFSET %s ', (offset,))
                    elif lim > 0:
                        cur.execute('SELECT modulus FROM "public"."public_key" '
                                    'WHERE "type" = \'RSA\' '
                                    'LIMIT %s ', (lim,))
                    else:
                        cur.execute('SELECT modulus FROM "public"."public_key" '
                                    'WHERE "type" = \'RSA\' ')
                    rows = cur.fetchall()
                    rows = np.array(rows)
                    rows = rows.reshape(-1)
                    rows = rows.tolist()
                    rows = [ZZ(i) for i in rows]
                    cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                return rows
