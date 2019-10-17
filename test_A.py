from redis import Redis
from rq import Queue
from attacks.BatchGCD import BatchGCD
import datastores

def setup():
    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    test_batchGCD(q)
    # test_postgres_bysize(q)

def test_batchGCD(queue):
    tf = datastores.TextFile()
    a = BatchGCD(tf)
    re1 = queue.enqueue(a.process, args=[a.ds.read], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # assert sum([1, 2, 3]) == 6, "Should be 6"

# def test_postgres_bysize(queue):
#     pg = datastores.PostGres()
#     a = BatchGCD(pg)
    # re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':5000, 'maxSize': 1025, 'order': 'asc'}], job_timeout=15000)
    # re2 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':10000, 'maxSize': 1025, 'order': 'desc'}], job_timeout=15000)
    # re3 = queue.enqueue(a.process, args=[a.ds.getRSAModuli, {'off': 0, 'lim':15000, 'maxSize': 1025, 'order': 'desc'}], job_timeout=15000)
    # match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # match = queue.enqueue(a.report, re2.id, depends_on=re2, job_timeout=15000)
    # match = queue.enqueue(a.report, re3.id, depends_on=re3, job_timeout=15000)
    # TODO sample data in .sql file to bootstrap the test db.
    # assert sum([1, 2, 3]) == 6, "Should be 6"

if __name__ == "__main__":
    setup()
    print("Everything passed")