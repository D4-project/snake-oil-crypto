from redis import Redis
from rq import Queue
import datastores
import attacks


def main():
    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    testDB(q)


def testChallenge(queue):
    r = datastores.TextFile()
    a = attacks.Tsage()
    res = queue.enqueue(a.process, r.moduli)
    queue.enqueue(a.report, res.id, depends_on=res)

def testDB(queue):
    pg = datastores.PostGres()
    r = pg.getRSA()
    a = attacks.Tsage()
    res = queue.enqueue(a.process, r, job_timeout=15000)
    queue.enqueue(a.report, res.id, depends_on=res, job_timeout=15000)
#    match = [x for x in zip(r, res.return_value) if x[1] != 1]
#    print("Matching keys in DB: {0}".format(len(match)))
#    print(match)

if __name__ == "__main__":
    main()
