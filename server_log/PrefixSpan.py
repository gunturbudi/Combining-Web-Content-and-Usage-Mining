#Info on the programmer
__author__ = "Perry D Christensen"
__date__ = "$18-04-2011 14:13:20$"

#imports inorder to run the program
import itertools
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.gudegnet
clusters = db.cluster_result

#Main method
def main():
    '''
    JIKA INPUT NYA DARI CLUSTER, 
    PREFIX SPAN DI PROSES PER CLUSTER
    '''
    cluster_d = clusters.distinct("cluster")
    for d in cluster_d:        
        input_sequence = populateDataClustered(d)
        pfs = Prefixspan(input_sequence, 3,'final_result/cluster_'+str(d))
    
    #input_sequence = populateDataClustered()
    #print input_sequence
    #input_sequence = [[0, 1, 2, 3, 4], [0, 1, 2, 3], [3, 2, 1, 2, 1, 2], [1, 2, 3, 2, 3, 1], [1, 2, 3, 1, 0, 1]]
    #pfs = Prefixspan(input_sequence, 3)
    
    
def populateDataClustered(cluster):
    print cluster
    input_sequence = []
    for row in clusters.find({"cluster":cluster}):
        input_sequence.append(row['topik'].split('|'))
    return input_sequence
        
        
    
def populateDataNoCluster():
    infile = open('visitor-ips.csv','r')
    input_sequence = []
    unik_topik = []
    for line in infile:
        sequence = []
        line = line.replace("[","").replace("]","").replace("'","")
        topics = line.split(',')
        for t in topics:
            if t.strip() not in unik_topik:
                unik_topik.append(t.strip())  
            seq = unik_topik.index(t.strip())
            #seq = t.strip()
            sequence.append(seq)
        input_sequence.append(sequence)
    outfile = open('unik_topik.csv', "w")
    for p in unik_topik:
        outfile.write("%s\t %s\n" % (str(unik_topik.index(p)),str(p)))
    outfile.close()
    return input_sequence
    
class Prefixspan:

    def __init__(self, S, supp, file_output):
        self.S = S
        self.supp = supp
        self.seq_pats = []
        self.freq = self.prefixspan([], 0, self.S)
        outfile = open(file_output, "w")
        for pat in self.seq_pats:
            outfile.write("%s\n" % str(pat))
        outfile.close()
        
        #print 'list of frequent sequences: ' + str(self.seq_pats)


    def prefixspan(self, a, l, S):
        '''
        All items in each sequence of the projected sequence database, S, are
        iterated to check for frequent items. Only the first instance in each
        sequence are taken into account.
        Items with a support count larger than the minimum support requirements
        (supp) are kept in a datastructure freq holding item and supportcount.
        '''
        #print S
        #print 'alpha (prefix) passed: ' + str(a)
        #print 'length \'l\' passed: ' + str(l)
        #print 'S_a (alphaprojected db) passed: ' + str(S)
        if not S:
            return a                                            #base case for recursion
        freq = {}
        for seq in S:
            tabu = []
            for item in seq:
                if item not in freq:
                    freq[item] = 1
                    tabu.append(item)
                elif item in tabu:       #tabu is used to ensure that only the first item in each sequence is taken into account
                    continue
                else:
                    freq[item] += 1
                    tabu.append(item)
        for k, v in freq.items():
            if v < self.supp:
                #print 'Deleting k, v: ' + str(k) + ', ' + str(v)
                del freq[k]                                     #array is iterated and frequent distinct length-1 sequential patterns are found
        #print 'frequent items ' + str(freq)
        '''
        All frequent items are appended to the prefix sequence alpha' (a_p) to
        be used for later generation of frequent sequences of length l+1.
        Furthermore frequent sequences of length l are appended to the set of
        all frequent sequences (seq_pats)
        '''
        if l == 0:
            a_p = [a + [k] for k, v in freq.items()]            #concatenate a with frequent items to generate new frequent sequential patterns of length 1
            freq2 = [([k], v) for k, v in freq.items()]
        else:
            for x in a:
                #print 'appending to prefix: ' + str(x)
                if len(x) == l:
                    a_p = [x + [k] for k, v in freq.items()]    #concatenate each frequent sequence with the frequent items from projected database
                    freq2 = [((x+[k]), v) for k, v in freq.items()]
        if not not freq2:                                       #as long as freq2 is not empty, append it to the overall list of frequent sequences
            [self.seq_pats.append(x) for x in freq2]
        #print 'new partitioned prefixes (alpha prime sequences): ' + str(a_p)
        '''
        The new projected database (suffix) are generated. Here the currently
        alpha projected db are reduced to contain only items subsequent to the
        current frequent item, thus iteratively reducing the size of the alpha
        projected db.
        '''
        suffix = []
        for k, v in freq.items():
            temp = []
            for seq in S:
                try:
                    i = seq.index(k)
                except:
                    i = 'false'                                 # False and 0 are the same value in python, I therefore need to make a pseudo-false value
                if i != 'false' and len(seq[i + 1:]) != 0:
                    temp.append(seq[i + 1:])                    #append all  items after i to temp
            suffix.append(temp)
        '''
        The new alpha projected database are passed in recursive calls to the
        prefixspan method along with the new prefix of length l+1.
        '''
        [self.prefixspan([alpha], l+1, a_proj_db) for (alpha, a_proj_db) in zip(a_p, suffix)]
        #print suffix

if __name__ == "__main__":
    main()