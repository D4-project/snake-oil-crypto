from redis import Redis
from rq import Queue
from attacks.BatchGCD import BatchGCD
from attacks.SearchGCD import SearchGCD
from builders.RSABuilder import RSABuilder
import datastores

def setup():
    redis_conn = Redis()
    # redis_conn = Redis('127.0.0.1', 6789, password='secret')
    q = Queue(connection=redis_conn)
    test_searchGCDFromModulus(q)
    #test_searchGCDFromIP(q)
    # test_postgres_bysize(q)

def test_batchGCD(queue):
    tf = datastores.TextFile()
    a = BatchGCD(tf)
    re1 = queue.enqueue(a.process, args=[a.ds.read], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    # assert sum([1, 2, 3]) == 6, "Should be 6"

def test_searchGCDFromModulus(queue):
    pg = datastores.PassivesslDB()
    modulus = 27724304371244874267063663458316042375388293362117516624328058162873845234849685034599507738102372559399923516291625203369809306864151467792423348537308628369862376050933753018273465837442442719693757564863601299614734955255152374884793253068172593987481611305254946983424159079692530544624855081287564139475305866286857797187581595819421389200392315106715642908698836633327578030142409357534660825175783393677528173786933800232969622955716519076748466236917882882274487196635346998385789302813729288257564056916750835167627352338432565102536554676437177815688058187786047090828196051984181517849637002136479208239269
    # modulus = pg.getRSAModuliByIP(dstIP = "60.243.245.99")
    print(modulus)
    a = SearchGCD(pg, modulus)
    b = RSABuilder(e = 65537, h = 'Box')
    re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Huawei'}], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    build = queue.enqueue(b.process, match.id, depends_on=match, job_timeout=15000)

def test_searchGCDFromIP(queue):
    with datastores.PassivesslDB() as pg:
        modulus = pg.getRSAModuliByIP(dstIP = "60.243.245.99")
    a = SearchGCD(pg, modulus[0])
    b = RSABuilder(e = 65537, h = 'Box')
    re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Huawei'}], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    build = queue.enqueue(b.process, match.id, depends_on=match, job_timeout=15000)

def test_searchGCD_forIP(queue):
    pg = datastores.PassivesslDB()
    a = SearchGCD(pg)
    b = RSABuilder(e = 65537, h = 'Box')
    re1 = queue.enqueue(a.process, args=[a.ds.getRSAModuliBySubject, {'subject':'Huawei'}], job_timeout=15000)
    match = queue.enqueue(a.report, re1.id, depends_on=re1, job_timeout=15000)
    build = queue.enqueue(b.process, match.id, depends_on=match, job_timeout=15000)

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
