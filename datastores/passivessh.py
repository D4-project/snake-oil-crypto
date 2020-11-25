from . import register_datastore
from . import DataStore
from configparser import ConfigParser
from tornado.httpclient import AsyncHTTPClient
from sage.all import *


@register_datastore
class PassiveSSH(DataStore):
    def __init__(self):
        super().__init__()
        self.name = "PassiveSSH datastore: stores SSH crytpo material from active scanning and passive monitoring"
        self.url = self.config['passivessh']['passivessh_url']
        self.username = self.config['passivessh']['username']
        self.pwd = self.config['passivessh']['password']

    def __enter__(self):
        print("entering passivessh")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        print("exiting passivessh")
        return True

    async def GetByFingerprint(self, fingerprint):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch('{}fingerprint/all/{}'.format(self.url, fingerprint),
                                               auth_mode="basic", auth_username=self.username, auth_password=self.pwd)
        except Exception as e:
            return ("Error: %s" % e)
        else:
            return (response.body)

    async def GetAllStats(self):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch('{}stats'.format(self.url),
                                               auth_mode="basic", auth_username=self.username, auth_password=self.pwd)
        except Exception as e:
            return ("Error: %s" % e)
        else:
            return (response.body)

