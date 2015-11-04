from urllib2 import urlopen
from json import load
import re, nltk,gensim
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)
from gensim import corpora, models, similarities, matutils
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
dictionary = corpora.Dictionary.load_from_text('gudegarticle_dict.txt')
my_corpus = gensim.corpora.MmCorpus('gudegarticlecorpus.mm')

def sym_kl(p,q):
    return np.sum([stats.entropy(p,q),stats.entropy(q,p)])

l = np.array([sum(cnt for _, cnt in doc) for doc in my_corpus])
def arun(corpus,dictionary,min_topics=1,max_topics=100,step=1):
    kl = []
    for i in range(min_topics,max_topics,step):
        lda = models.ldamodel.LdaModel(corpus=corpus,id2word=dictionary,num_topics=i, update_every=1, chunksize=10, passes=1)
        m1 = lda.expElogbeta
        U,cm1,V = np.linalg.svd(m1)
        #Document-topic matrix
        lda_topics = lda[my_corpus]
        m2 = matutils.corpus2dense(lda_topics, lda.num_topics).transpose()
        cm2 = l.dot(m2)
        cm2 = cm2 + 0.0001
        cm2norm = np.linalg.norm(l)
        cm2 = cm2/cm2norm
        kl.append(sym_kl(cm1,cm2))
    return kl
kl = arun(my_corpus,dictionary,max_topics=100)
 
# Plot kl divergence against number of topics
plt.plot(kl)
plt.ylabel('Symmetric KL Divergence')
plt.xlabel('Number of Topics')
plt.savefig('kldiv.png', bbox_inches='tight') 