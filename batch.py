from redis import Redis
from rq import Queue
from attacks.BatchGCD import BatchGCD
import datastores
import analyzers
import pdb

def main():
    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    # fun(q)
    facto(q)

def fun(q):
    pg = datastores.PostGres()
    a = BatchGCD(pg)

    FIA = []
    FIA.append[a.ds.getRSAModuli, {'off':0, 'lim':  25000}]
    FIA.append[a.ds.getRSAModuli, {'off':25001, 'lim':  50000}]
    FIA.append[a.ds.getRSAModuli, {'off':50001, 'lim':  75000}]
    FIA.append[a.ds.getRSAModuli, {'off':75001,  'lim': 100000}]
    FIA.append[a.ds.getRSAModuli, {'off':100001,  'lim': 125000}]
    FIA.append[a.ds.getRSAModuli, {'off':125001,  'lim': 150000}]
    FIA.append[a.ds.getRSAModuli, {'off':150001,  'lim': 175000}]
    FIA.append[a.ds.getRSAModuli, {'off':175001,  'lim': 200000}]

    q = []
    r = []
    p = []
    for i, m in enumerate(FIA):
        q.append(queue.enqueue(a.process, m , job_timeout=1500000))
        r.append(queue.enqueue(a.report, q[i].id, depends_on=q[i], job_timeout=150000))
        p.append(queue.enqueue(pg.pushResults, r[i].id, depends_on=r[i], job_timeout=30))


def facto(queue):
    pg = datastores.PassivesslDB()
    a = BatchGCD(pg)

    # re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Huawei', 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re2 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Lenovo', 'distinct': True}], job_timeout=15000)
    # re3 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Huawei', 'distinct': True, 'order': 'ASC'}], job_timeout=15000)
    # re4 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Lenovo'}], job_timeout=15000)

    # re3 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'TP-LINK'}], job_timeout=15000)
    # re4 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Netgear'}], job_timeout=15000)
    # re5 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Ubiquiti'}], job_timeout=15000)
    # re6 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'dlink'}], job_timeout=15000)
    # match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # match = queue.enqueue(a.report, re2.id, depends_on=re2, job_timeout=15000)
    # match = queue.enqueue(a.report, re3.id, depends_on=re3, job_timeout=15000)
    # match = queue.enqueue(a.report, re4.id, depends_on=re4, job_timeout=15000)
    # match = queue.enqueue(a.report, re5.id, depends_on=re5, job_timeout=15000)
    # match = queue.enqueue(a.report, re6.id, depends_on=re6, job_timeout=15000)

    # re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':25000, 'maxSize': 1025}], job_timeout=15000)
    # match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)

    # re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':50000, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re2 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 50001, 'lim':100000, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re3 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 100001, 'lim':150000, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)

    # re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':500, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re2 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 501, 'lim':500, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re3 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 1001, 'lim':500, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # match = queue.enqueue(a.report, re2.id, depends_on=re2, job_timeout=15000)
    # match = queue.enqueue(a.report, re3.id, depends_on=re3, job_timeout=15000)

    re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject': 'dlink', 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re2 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject': 'arlo', 'off': 501, 'lim':500, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    # re3 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject': 'dlink', 'off': 1001, 'lim':500, 'distinct': True, 'order': 'DESC'}], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # match = queue.enqueue(a.report, re2.id, depends_on=re2, job_timeout=15000)
    # match = queue.enqueue(a.report, re3.id, depends_on=re3, job_timeout=15000)


    # push = queue.enqueue(pg.pushResults, match.id, depends_on=match, job_timeout=1500)
    # shodan = queue.enqueue(sh.queryCertificate, match.id, depends_on=match, job_timeout=600)

if __name__ == "__main__":
    main()
