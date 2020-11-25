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

from JSONHandler import JSONHandler

from attacks.SearchGCD import SearchGCD

from sage.all import *

def initPlugins():
    dir(attacks)
    dir(datastores)
    dir(analyzers)
    dir(builders)
    dir(exporters)
    return True

class DatastoresStatus(JSONHandler):
    def get(self):
        status = []
        for k in datastores.DATASTORES:
            tmp = datastores.DATASTORES[k]()
            status.append({'name': k, 'description': tmp.name, 'status': 'ok'})
        self.write(json.dumps(status))


class AttacksStatus(JSONHandler):
    def get(self):
        status = []
        for k in attacks.ATTACKS:
            status.append({'name': k})
        self.write(json.dumps(status))


class AnalyzersStatus(JSONHandler):
    def get(self):
        status = []
        for k in analyzers.ANALYZERS:
            status.append({'name': k})
        self.write(json.dumps(status))


class BuildersStatus(JSONHandler):
    def get(self):
        status = []
        for k in builders.BUILDERS:
            status.append({'name': k})
        self.write(json.dumps(status))


class ExportersStatus(JSONHandler):
    def get(self):
        status = []
        for k in exporters.EXPORTERS:
            status.append({'name': k})
        self.write(json.dumps(status))

class Get_all_pssh_host_by_fingerprint(JSONHandler):
    async def get(self, q):
        pssh = datastores.PassiveSSH()
        response = await pssh.GetByFingerprint(q)
        self.write(response)

class Get_all_pssh_stats(JSONHandler):
    async def get(self):
        pssh = datastores.PassiveSSH()
        response = await pssh.GetAllStats()
        self.write(response)


class AttackBySSHFingerprint(JSONHandler):
    # GET should bring in the results
    # TODO switch GET and POST
    async def get(self,q):
        # Query PSSH to get the key material
        pssh = datastores.PassiveSSH()
        # Against PSSL
        pssl = datastores.PassivesslDB()
        response = await pssh.GetByFingerprint(q)
        j = json.loads(response)
        modulus = j['crypto_material']['modulus']
        a = SearchGCD(pssl, ZZ(modulus))
        re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject': 'Huawei'}], job_timeout=15000)
        match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
        self.write("Job Submitted")

    # POST should launch the attack


def make_app():
    # Basic endpoints
    application = tornado.web.Application([
        (r"/datastores/status", DatastoresStatus),
        (r"/datastores/passivessh/stats", Get_all_pssh_stats),

        (r"/datastores/passivessh/fingerprint/all/(.*)", Get_all_pssh_host_by_fingerprint),
        (r"/attacks/status", AttacksStatus),
        (r"/analyzers/status", AnalyzersStatus),
        (r"/builders/status", BuildersStatus),
        (r"/exporters/status", ExportersStatus),

        (r"/attacks/all/ssh/fingerprint/(.*)", AttackBySSHFingerprint),
        # (r"/datastores/passivessh/banners",Get_all_banner),
        # (r"/datastores/passivessh/banner/hosts/(.*)",Get_all_banner_by_host),
        # (r"/datastores/passivessh/keys/types",get_all_keys_types), # show nb ?
        # (r"/datastores/passivessh/host/ssh/(.*)", Get_host),
        # (r"/datastores/passivessh/host/history/(.*)",Get_host_history), # remove host from url path ?
        # (r"/datastores/passivessh/fingerprints", Get_fingerprints_stats),
        # (r"/datastores/passivessh/hasshs", Get_all_hassh),
        # (r"/datastores/passivessh/hassh/hosts/(.*)", Get_hosts_by_hassh),
    ])

    return application

if __name__ == "__main__":
    # Init plugins
    initPlugins()
    # SnakeOil redis connection
    redis_conn = Redis()
    queue = Queue(connection=redis_conn)

    # Tornado web server
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()