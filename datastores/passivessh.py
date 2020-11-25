from . import register_datastore
from . import DataStore
from configparser import ConfigParser
from tornado.httpclient import AsyncHTTPClient
from sage.all import *

@register_datastore
class PassiveSSH(DataStore):
    def __init__(self):
        self.name = "PassiveSSH datastore: stores SSH crytpo material from active scanning and passive monitoring"
        # Config
        self.params = self.config()

    def __enter__(self):
        print("entering passivessh")
        return self

    def __exit__(self ,exc_type, exc_value, tb):
        print("exiting passivessh")
        return True

    def config(self, filename='config.conf', section='passivessh'):
        parser = ConfigParser()
        parser.read(filename)
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                return param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    async def getByFingerprint(self, fingerprint):
        print('{}fingerprint/all/{}'.format(self.params, fingerprint))
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch('{}fingerprint/all/{}'.format(self.params, fingerprint))
        except Exception as e:
            return("Error: %s" % e)
        else:
            return(response.body)
