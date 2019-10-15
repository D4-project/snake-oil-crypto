from . import register_datastore
from . import DataStore
from configparser import ConfigParser
from sage.all import *

@register_datastore
class TextFile(DataStore):
    def __init__(self):
        self.name = "Text file datastore: reads RSA moduli from CR separated text file"
        # read textfile parameters
        self.filename = self.config()['path']
        if not os.path.exists(self.filename):
            raise Exception('{0} does not exist'.format(self.filename))

    def __enter__(self):
        self.openedfile = os.open(self.filename, 'r')
        return self

    def __exit__(self ,exc_type, exc_value, tb):
        self.openedfile.close()
        if exc_type is not None:
            return False
        return True

    def config(self, filename='config.conf', section='textfile'):
        parser = ConfigParser()
        parser.read(filename)
        file = {}
        if parser.has_section(section):
            file = parser.items(section)
            for param in file:
                file[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return file

    def read(self):
        try:
            rows = []
            for line in fp:
                rows.append(ZZ('0x'+(line.strip())))
            return rows
        except IOError:
            raise Exception('Could not read {0}.'.format(self.filename))
