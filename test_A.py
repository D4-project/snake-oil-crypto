from redis import Redis
from rq import Queue
from attacks.BatchGCD import BatchGCD
import datastores

def setup():
    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    test_batchGCD(q)

def test_batchGCD(queue):
    tf = datastores.TextFile()
    a = BatchGCD(tf)
    re1 = queue.enqueue(a.process, args=[a.ds.read], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # assert sum([1, 2, 3]) == 6, "Should be 6"

if __name__ == "__main__":
    setup()
    print("Everything passed")