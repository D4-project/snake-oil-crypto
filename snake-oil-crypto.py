import datastores
import attacks


def main():
    testChallenge()
    testDB()

def testChallenge():
     # quick test
    print("Matching keys in Challenge file:")
    r = datastores.TextFile()
    a = attacks.Tsage()
    res = a.process(r.moduli)
    match = [x for x in zip(r.moduli, res) if x[1] != 1]
    print("Matching keys in TextFile: {0}".format(len(match)))
    print(match)


def testDB():
    pg = datastores.PostGres()
    r = pg.getRSA()
    a = attacks.Tsage()
    res = a.process(r)
    match = [x for x in zip(r, res) if x[1] != 1]
    print("Matching keys in DB: {0}".format(len(match)))
    print(match)


if __name__ == "__main__":
    main()
