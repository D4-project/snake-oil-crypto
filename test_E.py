from redis import Redis
from rq import Queue
from attacks.BatchGCD import BatchGCD
from exporters.MISPE import MISPE
import datastores

def setup():
    redis_conn = Redis()
    AT = Queue('Attacks', connection=redis_conn)
    EX = Queue('MISP Exports', connection=redis_conn)
    test_MISP_Export(AT, EX)


def test_MISP_Export(AT, EX):
    # tf = datastores.TextFile()
    tf = datastores.PassivesslDB()
    e = MISPE(tf)


if __name__ == "__main__":
    setup()
    print("Everything passed")
