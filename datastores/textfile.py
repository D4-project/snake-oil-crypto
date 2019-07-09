from . import register_datastore
from . import DataStore
from configparser import ConfigParser
import os
from sage.all import *

@register_datastore
class TextFile(DataStore):
    def __init__(self):
        self.name = "Read RSA moduli from CR separated text file"
        self.moduli = self.read()

    def config(self, filename='config.conf', section='textfile'):
        parser = ConfigParser()
        # read config file
        parser.read(filename)
        file = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                file[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return file

    def read(self):

        file = self.config()

        if os.path.exists(file['path']):
            with open(file['path'], 'r') as fp:
                try:
                    rows = []
                    for line in fp:
                        rows.append(ZZ('0x'+(line.strip())))
                    return rows
                except IOError:
                    raise Exception('Could not read {0}.'.format(file['path']))
