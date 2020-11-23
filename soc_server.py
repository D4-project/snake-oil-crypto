from redis import Redis
from rq import Queue

import datastores
import attacks
import builders
import analyzers
import exporters

import json
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class DatastoresStatus(tornado.web.RequestHandler):
    def get(self):
        # List available datastores and give their status
        dir(datastores)
        status = []
        for k in datastores.DATASTORES:
            tmp = datastores.DATASTORES[k]()
            status.append({'name': k, 'description': tmp.name, 'status': 'ok'})
        self.write(json.dumps(status))

class AttacksStatus(tornado.web.RequestHandler):
    def get(self):
        # List available Attacks
        dir(attacks)
        status = []
        for k in attacks.ATTACKS:
            status.append({'name': k})
        self.write(json.dumps(status))

class AnalyzersStatus(tornado.web.RequestHandler):
    def get(self):
        # List available Analyzers
        dir(analyzers)
        status = []
        for k in analyzers.ANALYZERS:
            status.append({'name': k})
        self.write(json.dumps(status))


class BuildersStatus(tornado.web.RequestHandler):
    def get(self):
        # List available Builders
        dir(builders)
        status = []
        for k in builders.BUILDERS:
            status.append({'name': k})
        self.write(json.dumps(status))


class ExportersStatus(tornado.web.RequestHandler):
    def get(self):
        # List available Exporter
        dir(exporters)
        status = []
        for k in exporters.EXPORTERS:
            status.append({'name': k})
        self.write(json.dumps(status))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/datastores/status", DatastoresStatus),
        (r"/attacks/status", AttacksStatus),
        (r"/analyzers/status", AnalyzersStatus),
        (r"/builders/status", BuildersStatus),
        (r"/exporters/status", ExportersStatus),
    ])

if __name__ == "__main__":
    # SnakeOil redis connection
    redis_conn = Redis()
    q = Queue(connection=redis_conn)

    # Tornado web server
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()