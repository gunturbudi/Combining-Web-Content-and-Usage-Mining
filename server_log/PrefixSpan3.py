from collections import defaultdict

def populateData():
    infile = open('visitor-ips.csv','r')
    input_sequence = []
    unik_topik = []
    for line in infile:
        sequence = []
        line = line.replace("[","").replace("]","").replace("'","")
        topics = line.split(',')
        for t in topics:
            if t.strip not in unik_topik:
                unik_topik.append(t.strip())            
            sequence.append(unik_topik.index(t.strip()))
        input_sequence.append(sequence)
    print input_sequence

'''
db = [
    [0, 1, 2, 3, 4], [0, 1, 2, 3], [3, 2, 1, 2, 1, 2], [1, 2, 3, 2, 3, 1], [1, 2, 3, 1, 0, 1]
]
'''

db = populateData()

minsup = 2

results = []


def mine_rec(patt, mdb):
    def localOccurs(mdb):
        occurs = defaultdict(list)

        for (i, stoppos) in mdb:
            seq = db[i]
            for j in range(stoppos, len(seq)):
                l = occurs[seq[j]]
                if len(l) == 0 or l[-1][0] != i:
                    l.append((i, j + 1))

        return occurs

    for (c, newmdb) in localOccurs(mdb).items():
        newsup = len(newmdb)

        if newsup >= minsup:
            newpatt = patt + [c]

            results.append((newpatt, [i for (i, stoppos) in newmdb]))
            mine_rec(newpatt, newmdb)

mine_rec([], [(i, 0) for i in range(len(db))])

print(results)