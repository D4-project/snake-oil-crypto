#!/usr/bin/env sage -python
from . import register_analyzer
from . import Analyzer
from rq import Queue, Connection
from redis import Redis
from sage.all import *
from shodan import Shodan

@register_analyzer
class ShodanA(Analyzer):

    def queryCertificate(self, X):
        self.api = Shodan(self.config['CREDENTIALS']['KEY'])
        for borked in X:
            results = self.api.search('ssl:'+'"'+borked[]+'"')
            # results = self.api.search('ssl:'+'"'+borked+'"')
            print(results)

    # def subscribe(self):
    #     try:
    #         for banner in self.api.stream.ports([443, 8443]):
    #             if 'ssl' in banner:
    #                 Print out all the SSL information that Shodan has collected
    #                 print(banner['ssl'])
                    # print(banner)
        # except Exception as e:
        #     print('Error: {}'.format(e))
