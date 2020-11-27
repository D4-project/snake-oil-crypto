from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

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
        # First check whether there is an existing job for this request
        # exceptions drives my logic flow because I :love: python /s
        try:
            job = Job.fetch("{}".format(q), connection=redis_conn)
            result = {}
            result['status'] = job.get_status()
            if res := job.result:
                if len(res) == 3:
                    result['success'] = true
                    result['modulus'] = "{}".format(res[1])
                    result['divisor'] = "{}".format(res[2])
            else:
                result['success'] = false
            self.write(json.dumps(result))
        except NoSuchJobError:
            jobttl = 20
            # Query PSSH to get the key material
            pssh = datastores.PassiveSSH()
            # Against PSSL
            pssl = datastores.PassivesslDB()
            response = await pssh.GetByFingerprint(q)
            j = json.loads(response)
            modulus = j['crypto_material']['modulus']
            # dlink router
            # modulus = 127720680654041728988985021844570374903129750412991740869975622165089966135003475385309906950769680678872760535596422216617941097583542103453771389228244387590996637297307783781075096418281063367358534118134965144898414681177759402415323202118081569413921873174724188498911880892541949556552524435767369304297
            a = SearchGCD(pssl, ZZ(modulus))
            # TODO make TTL configurable
            #  re1 = qsshf.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':500000, 'maxSize': 4096, 'order': 'asc'}], job_timeout=15000, result_ttl = -1)
            re1 = qsshf.enqueue(a.process,
                                args=[a.ds.getRSAModuli, {'off': 0, 'lim': 500000, 'maxSize': 4096, 'order': 'asc'}],
                                job_timeout=15000, result_ttl=jobttl, job_id="{}".format(q))
            self.write(json.dumps({'submitted': True, 'jobid': re1.id, 'ttl':jobttl}))

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
    # TODO use the config file for redis connection and jobttl

    # Init plugins
    initPlugins()
    # SnakeOil redis connection
    redis_conn = Redis()
    qsshf= Queue(name="ssh-fingerprint",connection=redis_conn)

    # Tornado web server
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()