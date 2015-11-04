import sys,datetime, pycountry,re,gensim,operator,numpy,pymongo
from langdetect import detect
from pytz import country_names
from gensim import corpora, models, similarities
from numpy import *
from minisom import MiniSom
from pylab import plot,axis,show,pcolor,colorbar,bone
import matplotlib.pyplot as plt
import settings
import gc
from random import randint

ipDict = {}
session = {}
uniqueUrl = set()
noTopicUrl = set()
userAgentUnique = set()
rootUrl = settings.rootUrl
db = settings.db
articles = settings.articles
no_uji = 1

class Prefixspan:
    def __init__(self, S, supp, file_output):
        self.S = S
        self.supp = supp
        self.seq_pats = []
        self.freq = self.prefixspan([], 0, self.S)
        self.saveFinalResult(file_output,self.seq_pats)
        #print 'list of frequent sequences: ' + str(self.seq_pats)
        
    def saveFinalResult(self,file_output,seq_pat):
        pref_result = db.prefix_result
        print "Saving Final Result Prefixspan.."
        pref_save = []
        for pat in self.seq_pats:
            pref_save.append({"cluster":file_output,"sequence":pat[0],"min_sup":pat[1],"data_uji":no_uji})

        self.seq_pats = []
        try:
            print "Menyimpan PrefixSpan..."
            pref_result.insert_many(pref_save) 
            pref_save = []
            print "Berhasil Penyimpanan"
            pref_result.create_index([("cluster", pymongo.ASCENDING),("data_uji", pymongo.ASCENDING)])
            print "Berhasil Buat Index PrefixResult"
        except:
            print "Error Penyimpanan"
    
        
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
        if(l >= 16):
            print "Done"
            return a

        print 'length \'l\' passed: ' + str(l)
        #print 'S_a (alphaprojected db) passed: ' + str(S)
        if not S:
            print "Done"
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
    
def create_corpus(number_topic):
    #enchant.set_param("enchant.myspell.dictionary.path",r"C:\Python278\Lib\site-packages\enchant\share\enchant\myspell")
    #d = enchant.Dict("id_ID")
    #d_en = enchant.Dict("en_US")

    print "Starting Process.."
    #BAHASA INDONESIA
    stop = open('lda/stoplist-bahasa')
    print "Pembacaan Stoplist.."
    stopstr = stop.readline()    
    
    docset = []
    print "Pembuatan Docset Indonesia.."
    for article in list(articles.find({'lang':'id'})):
        artic = re.sub(r'([^\s\w]|_)+', '', article['article'])
        docset.append(artic)
    print "Pembuatan Docset Indonesia Berhasil.."
    
    print "Penghilangan Stopword Indonesia.."
    stoplist = set(stopstr.split())
    
    texts = [[word for word in document.lower().split() if (word not in stoplist and len(word)>1 and is_number(word)==False)] for document in docset]
    all_tokens = ''.join(str(v) for v in texts)
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once] for text in texts]
    print "Penghilangan Stopword Indonesia Berhasil.."
    
    
    print "Pembuatan Dictionary dan Corpus Indonesia.."
    dictionary = corpora.Dictionary(texts)
    dictionary.save('lda/gudegarticle.dict')
    dictionary.save_as_text('lda/gudegarticle_dict.txt')
    print "Berhasil Membuat Dictionary Indonesia"
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('lda/gudegarticlecorpus.mm', corpus) # store to disk, for later use
    print "Berhasil Membuat Corpus Indonesia"
    
    print "Pembuatan Model LDA Bahasa Indonesia.."
    id2word = gensim.corpora.Dictionary.load_from_text('lda/gudegarticle_dict.txt')
    mm = gensim.corpora.MmCorpus('lda/gudegarticlecorpus.mm')
    number_of_topic = int(number_topic)
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=number_of_topic, update_every=5, eval_every=1,chunksize=10, passes=1)
    print "Berhasil Membuat Model LDA Bahasa Indonesia"
    
    lda.save('lda/model_gudeg')
    
    
    stop = open('lda/stoplist-english')
    print "Pembacaan Stoplist Bahasa Inggris.."
    stopstr = stop.readline()
    
    docset = []
    print "Pembuatan Docset English.."
    for article in list(articles.find({'lang':'en'})):
        artic = re.sub(r'([^\s\w]|_)+', '', article['article'])
        docset.append(artic)
    print "Pembuatan Docset English Berhasil"
    
    print "Penghilangan Stopword English.."
    stoplist = set(stopstr.split())
    texts = [[word for word in document.lower().split() if (word not in stoplist and len(word)>1 and is_number(word)==False)] for document in docset]
    all_tokens = ''.join(str(v) for v in texts)
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once] for text in texts]
    print "Penghilangan Stopword English Berhasil"
    
    print "Pembuatan Dictionary dan Corpus English"
    
    dictionary = corpora.Dictionary(texts)
    dictionary.save('lda/gudegarticle_en.dict')
    dictionary.save_as_text('lda/gudegarticle_dict_en.txt')
    print "Berhasil Membuat Dictionary English"
    
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('lda/gudegarticlecorpus_en.mm', corpus) # store to disk, for later use
    print "Berhasil Membuat Corpus English"
    
    print "Membuat Model LDA English"
    
    id2word = gensim.corpora.Dictionary.load_from_text('lda/gudegarticle_dict_en.txt')
    mm = gensim.corpora.MmCorpus('lda/gudegarticlecorpus_en.mm')
    number_of_topic = int(number_topic)
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=number_of_topic, update_every=5, eval_every=1,chunksize=10, passes=1)
    
    lda.save('lda/model_gudeg_en')
    print "Berhasil Membuat LDA Model English"
    
    html = '<div role="alert" class="alert alert-success alert-dismissible fade in">'
    html = html + ' <button aria-label="Close" data-dismiss="alert" class="close" type="button"><span aria-hidden="true">Close</span></button>'
    html = html + '  Creating LDA Model Language : Indonesian and English Success!</div>'
    return html

def see_model(number_topic,lang):
    file_model = ""
    if lang=="id":
        file_model = "lda/model_gudeg"
    elif lang=="en":
        file_model = "lda/model_gudeg_en"
    lda = gensim.models.LdaModel.load(file_model)
    top_add = ""
    if(lang=="en"):
        top_add ="en"
    model_str = ""
    for i in range(int(number_topic)):
        model_str = model_str + " Topik " + str(i+1) + " : " + str(lda.print_topic(i)) + "\n \n"
    
    print model_str
    return model_str

def get_article(topic):
    html = "<button type='button' onclick='nextArticle(\""+str(topic)+"\")' class='btn btn-success btn-sm'> Next Article </button><br/>"
    
    if(is_number(topic)):
        topic = int(topic)
    else:
        topic = str(topic)
    count_article = articles.find({"topic":topic}).count()
    article = articles.find({"topic":topic}).limit(-1).skip(randint(1,count_article)).next()
    html = html + "<a target='_blank' class='btn btn-default btn-xs' href='"+article['url']+"'>Article Link</a><br/>"
    html = html + "<p>" + article["article"] + "</p>"
    return html

#source http://www.seehuhn.de/blog/52
def parseLog(line):
    parts = [
        r'(?P<host>\S+)',                   # host %h
        r'\S+',                             # indent %l (unused)
        r'(?P<user>\S+)',                   # user %u
        r'\[(?P<time>.+)\]',                # time %t
        r'"(?P<request>.+)"',               # request "%r"
        r'(?P<status>[0-9]+)',              # status %>s
        r'(?P<size>\S+)',                   # size %b (careful, can be '-')
        r'"(?P<referer>.*)"',               # referer "%{Referer}i"
        r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
    ]
    pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
    m = pattern.match(line)
    res = m.groupdict()
    
    return res


def assign_topic():
    lda = gensim.models.LdaModel.load('lda/model_gudeg')    
    dicts = corpora.Dictionary.load_from_text('lda/gudegarticle_dict.txt')    
    for article in list(articles.find({'lang':'id'})):
        artic = re.sub(r'([^\s\w]|_)+', '', article['article'])
        result = lda[dicts.doc2bow(artic.lower().split())]
        maxs = 0
        topic_selected = 0
        for res in result:
            if res[1]>maxs:
                maxs=res[1]
                topic_selected = res[0]
        #print "Topik : ", topic_selected, " dengan nilai ",max, " ==> ",result
        #article_indo.insert({"url":article['url'],'article':article['article'],'topik':topic_selected});
        articles.update({"_id":article['_id']},{"$set":{'topic':topic_selected}})
    print "Assign Topik ke Artikel Bahasa Indonesia Berhasil Dilakukan! \n"
    
    lda = gensim.models.LdaModel.load('lda/model_gudeg_en')
        
    dicts = corpora.Dictionary.load_from_text('lda/gudegarticle_dict_en.txt')
    
    for article in list(articles.find({'lang':'en'})):
        artic = re.sub(r'([^\s\w]|_)+', '', article['article'])
        result = lda[dicts.doc2bow(artic.lower().split())]
        maxs = 0
        topic_selected = 0
        for res in result:
            if res[1]>maxs:
                maxs=res[1]
                topic_selected = res[0]
        #print "Topik : ", topic_selected, " dengan nilai ",max, " ==> ",result
        #article_indo.insert({"url":article['url'],'article':article['article'],'topik':topic_selected});
        articles.update({"_id":article['_id']},{"$set":{'topic':"en"+str(topic_selected)}})
        
        
    print "Assign Topik ke Artikel Bahasa Inggris Berhasil Dilakukan!"
    
    html = '<div role="alert" class="alert alert-success alert-dismissible fade in">'
    html = html + ' <button aria-label="Close" data-dismiss="alert" class="close" type="button"><span aria-hidden="true">Close</span></button>'
    html = html + '  Assigning Topic Success!</div>'
    return html

def cleanLog(infileName):
    recordsRead = 0
    sessionNumber = 0
    progressThreshold = 100

    infile = open(infileName, "r")
    cleaned_file = open(str(infileName)+"_clean","w")

    for line in infile:
        if (line[0] == '#'):
            continue
        else:
            recordsRead += 1
            try:
                regresult = parseLog(line)
            except AttributeError:
                print line
                continue
            
            if (recordsRead >= progressThreshold):
                print "Read %d records" % recordsRead
                progressThreshold *= 2

            request = regresult['request'].split()
            date_access = regresult['time'].split()
            
            try:
                accessUrl = request[1]
            except IndexError:
                print regresult['request']
                accessUrl = regresult['request']
                
            theDate,ipAddr, userAgent, statusCode = date_access[0],regresult['host'], regresult['agent'], regresult['status']
            
            #PENHILANGAN BERDASASRKAN EXTENSION
            regexp = re.compile(r'\.css|\.js|\.ico|\.woff|\.png|\.jpg|\.gif|\.svg|\.xbm|\.JPG|\.xml|\.rss|\.swf|\.ttf|\.txt')            
            if regexp.search(accessUrl) is not None:
                continue
            
            #PENGHILANGAN BERDASARKAN PAGE
            regexp = re.compile(r'PageNo|personal.html|search_|personal.php|dir_logo')
            if regexp.search(accessUrl) is not None:
                continue
            
            #PENGHILANGAN SELAIN NEWS DAN DIRECTORY
            regexp = re.compile(r'directory')
            if regexp.search(accessUrl) is None:
                continue
            
            #HANYA AMBIL YANG STATUS CODE 200
            regexp = re.compile(r'200')
            if regexp.search(statusCode) is None:
                continue
            
            
            #CEK BOT / SPIDER
            userAgentUnique.add(userAgent) 
            regexp = re.compile(r'bingbot|spider|Baiduspider|GrapeshotCrawler|Googlebot|Mail.RU_Bot|YandexBot|Exabot|MJ12bot|LivelapBot|AhrefsBot|WeSEE|DotBot|XoviBot|Insitesbot|linkdexbot|AddThis.com|Yeti/1.1|Twitterbot|TweetmemeBot')
            if regexp.search(userAgent) is not None:
                continue

            cleaned_file.write(line)



def processLog(infileName):
    global session
    ipDict = {}    
    session = {}
    uniqueUrl = set()
    noTopicUrl = set()
    userAgentUnique = set()

    infile = open(infileName, "r")

    recordsRead = 0
    sessionNumber = 0
    progressThreshold = 100
    sessionTimeout = datetime.timedelta(minutes=30)
    

    for line in infile:
        #print line
        if (line[0] == '#'):
            continue
        else:
            recordsRead += 1
            try:
                regresult = parseLog(line)
            except AttributeError:
                print line
                continue
        
            #fields = line.split()
            
            #if recordsRead == 1000:
            #    break
            
            if (recordsRead >= progressThreshold):
                print "Read %d records" % recordsRead
                progressThreshold *= 2

            #theDate = fields[3]
            #ipAddr, userAgent, accessUrl, statusCode = fields[0], fields[-1], fields[6], fields[8]
            request = regresult['request'].split()
            date_access = regresult['time'].split()
            
            try:
                accessUrl = request[1]
            except IndexError:
                print regresult['request']
                accessUrl = regresult['request']
                
            theDate,ipAddr, userAgent, statusCode = date_access[0],regresult['host'], regresult['agent'], regresult['status']
            
            #print fields
            #print ipAddr + " || " + userAgent + " || " + accessUrl + " || " + statusCode + "\n"
            #if (recordsRead is 10):
            #    sys.exit()
            
            #PENHILANGAN BERDASASRKAN EXTENSION
            regexp = re.compile(r'\.css|\.js|\.ico|\.woff|\.png|\.jpg|\.gif|\.svg|\.xbm|\.JPG|\.xml|\.rss|\.swf|\.ttf|\.txt')            
            if regexp.search(accessUrl) is not None:
                continue
            
            #PENGHILANGAN BERDASARKAN PAGE
            regexp = re.compile(r'PageNo|personal.html|search_|personal.php|dir_logo')
            if regexp.search(accessUrl) is not None:
                continue
            
            #PENGHILANGAN SELAIN NEWS DAN DIRECTORY
            regexp = re.compile(r'directory')
            if regexp.search(accessUrl) is None:
                continue
            
            #HANYA AMBIL YANG STATUS CODE 200
            regexp = re.compile(r'200')
            if regexp.search(statusCode) is None:
                continue
            
            
            #CEK BOT / SPIDER
            userAgentUnique.add(userAgent) 
            regexp = re.compile(r'bingbot|spider|Baiduspider|GrapeshotCrawler|Googlebot|Mail.RU_Bot|YandexBot|Exabot|MJ12bot|LivelapBot|AhrefsBot|WeSEE|DotBot|XoviBot|Insitesbot|linkdexbot|AddThis.com|Yeti/1.1|Twitterbot|TweetmemeBot')
            if regexp.search(userAgent) is not None:
                continue
               
            newRequestTime = datetime.datetime.strptime(theDate, "%d/%b/%Y:%H:%M:%S")
            
            articles = db.article_directory

            
            topic = articles.find_one({"url":rootUrl+accessUrl},{"topic":1})
            if topic is not None:
                accessUrl = "Topik "+str(topic['topic'])
            else:                
                noTopicUrl.add(accessUrl)
                continue
            
            uniqueUrl.add(accessUrl)
            
            if ipAddr not in ipDict:
                ipDict[ipAddr] = {userAgent: [1, newRequestTime]}                
                sessionNumber+=1
                session[sessionNumber] = [accessUrl]
            else:
                if userAgent not in ipDict[ipAddr]:
                    ipDict[ipAddr][userAgent] = [1, newRequestTime]
                    sessionNumber+=1
                    session[sessionNumber] = [accessUrl]              
                else:
                    ipdipaua = ipDict[ipAddr][userAgent]
                    if newRequestTime - ipdipaua[1] >= sessionTimeout or len(session[sessionNumber])>10:
                        ipdipaua[0] += 1
                        sessionNumber+=1
                        session[sessionNumber] = [accessUrl]
                    else:
                        session[sessionNumber].append(accessUrl)
                    ipdipaua[1] = newRequestTime
            
    
    return recordsRead

def saveSessions():
    db.session_log.remove({"data_uji":no_uji})
    print "Menyimpan Session Data Uji " + str(no_uji)
    session_log_db = db.session_log
    for key,value in session.iteritems():        
        session_seq = []
        for val in value:
            session_seq.append(val)
        session_log_db.insert({"key":(key-1),"session":session_seq,"data_uji":no_uji})


def sessionization(log_data):
    print "Sessionization pada Data Uji " + str(no_uji)
    
    processLog(log_data)
    saveSessions()
    html = '<div role="alert" class="alert alert-success alert-dismissible fade in">'
    html = html + ' <button aria-label="Close" data-dismiss="alert" class="close" type="button"><span aria-hidden="true">Close</span></button>'
    html = html + 'Process Success!</div>'
    return html


def flatten(matrix):
    flat_matrix = []
    for a in matrix:
        flat_matrix.extend(a)
    return flat_matrix

def getPresedenceMatrix(seq,unique,flatting):
    seq.insert(0,0)
    seq.append(0)
    unique.insert(0,0)
    
    matrix = []

    for a in range(0,len(unique)):
        temp = []
        for b in range(0,len(unique)):
            temp.append(0)
        matrix.append(temp)

    for i in range(0,len(seq)):
        for j in range(i+1,len(seq)):
            matrix[seq[i]][seq[j]] = matrix[seq[i]][seq[j]] + 1

    for a in range(0,len(unique)):
        jml = float(sum(matrix[a]))
        for b in range(0,len(unique)):
            if jml!=0:
                matrix[a][b] = float(matrix[a][b]) / jml
            else:
                matrix[a][b] = 0

    if(flatting):
        matrix = flatten(matrix)

    unique.remove(0)
    return matrix

def convertSession(sessionLog,uniqueTopic):
    sess = []
    for s in sessionLog:
        sess.append(uniqueTopic.index(s)+1)
    return sess


def train_som(alpha_som,omega_som):
    print "SOM pada Data Uji " + str(no_uji)
 
    session_log_db = db.session_log
    allTopic = articles.distinct("topic")
    
    uniqueTopic = []
    for t in allTopic:
        uniqueTopic.append("Topik " + str(t).strip())
    
    lentopic = len(uniqueTopic)

    panjangSOM = session_log_db.find({"data_uji":no_uji}).count()
    lebarSOM = lentopic*lentopic + lentopic*2 + 1
    
    
    somInput = []
    for s in session_log_db.find({"data_uji":no_uji}):
        matrixSOM = getPresedenceMatrix(convertSession(s["session"],uniqueTopic),uniqueTopic,1)
        somInput.append(matrixSOM)

    numpy.matrix(somInput)
    SOM(somInput,lebarSOM,panjangSOM,alpha_som,omega_som)    
        
    return "Berhasil Melakukan Training SOM"

def test_som(alpha_som,omega_som):
    
    print "Clustering pada Data Uji " + str(no_uji)
    
    session_log_db = db.session_log
    allTopic = articles.distinct("topic")
    lentopic = len(allTopic)
    uniqueTopic = []
    for t in allTopic:
        uniqueTopic.append("Topik " + str(t).strip())
    
    lebarSOM = lentopic*lentopic + lentopic*2 + 1
    panjangSOM = session_log_db.find({"data_uji":no_uji}).count()
    #somInput = zeros((panjangSOM,lebarSOM),dtype=int16)
    somInput = []
    oriSess = []
    for s in session_log_db.find({"data_uji":no_uji}):
        somInput.append(getPresedenceMatrix(convertSession(s["session"],uniqueTopic),uniqueTopic,1))
        oriSess.append(s["session"])

    
    som = MiniSom(16,16,lentopic,sigma=omega_som,learning_rate=alpha_som)
    som.weights = numpy.load('weight_som.npy')
    #print som.weights
    outfile = open('cluster-result.csv','w')
    seq_number = 0
    cluster_mongo = db.cluster_result
    cluster_mongo.remove({"data_uji":no_uji})
    for cnt,xx in enumerate(somInput):
        w = som.winner(xx) # getting the winner
        outfile.write("%s " % str(("|".join(oriSess[seq_number]))))
        outfile.write("%s-%s \n" % (str(w[0]),str(w[1])))
        cluster_mongo.insert({"topik":"|".join(oriSess[seq_number]),"cluster":(str(w[0])+"-"+str(w[1])),"data_uji":no_uji})
        seq_number = seq_number + 1
    outfile.close()
    #TopikCluster()
    
    return "Berhasil Melakukan Clustering"

def see_som_map():
    clusters = db.cluster_result
    
    map_html = "<table border=1>"
    for i in range(16):
        map_html = map_html + "<tr>"
        for j in range(16):
            cluster_label = str(i)+"-"+str(j)
            count_cluster = clusters.find({'cluster':cluster_label,'data_uji':no_uji}).count()
            if count_cluster > 0:
                map_html = map_html + "<td style='text-align:center;width:30px;height:30px'><a href='#' onclick=getSomResult('"+cluster_label+"')>"+str(count_cluster)+"</a></td>"
            else:
                map_html = map_html + "<td style='text-align:center;width:30px;height:30px'>"+str(count_cluster)+"</td>"
        map_html = map_html + "</tr>"
    map_html = map_html+"</table>"
    return map_html

def get_som_result(cluster):
    html_som = "<ol>"
    clusters = db.cluster_result
    for pref in clusters.find({"cluster":cluster,'data_uji':no_uji}):
        html_som = html_som + ("<li>" + str(pref["topik"])+"</li>")
    
    html_som = html_som + "</ol>"
    return html_som
    
    
def do_prefixSpan(min_support):
    print "PrefixSpan pada Data Uji " + str(no_uji)
    
    print "Creating Index..."
    db.cluster_result.create_index([("cluster", pymongo.ASCENDING),("data_uji", pymongo.ASCENDING)])
    
    clusters = db.cluster_result
    pref_result = db.prefix_result
    
    print "PrefixSpan Running"
    cluster_d = clusters.find({"data_uji":no_uji}).distinct("cluster")
    for d in cluster_d:        
        input_sequence = populateDataClustered(d)
        Prefixspan(input_sequence, min_support,str(d))
    
    return "Berhasil Melakukan Sequence Pattern Mining dengan PrefixSpan"

def do_prefixSpan_khusus():
    min_support = 3
    no_uji = 0
    print "PrefixSpan pada Data Uji " + str(no_uji)
    print "Creating Index..."

    clusters = db.cluster_result
    pref_result = db.prefix_result
    
    print "PrefixSpan Running"
    cluster_d = clusters.find({"data_uji":no_uji}).distinct("cluster")
    for d in cluster_d:
        res = pref_result.find({"data_uji":no_uji,"cluster":d}).count()
        print res
        if res>0:
            continue
        else:
            input_sequence = populateDataClustered(d)
            Prefixspan(input_sequence, min_support,str(d))
    
    return "Berhasil Melakukan Sequence Pattern Mining dengan PrefixSpan"

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def SOM(data,leninput,lentarget,alpha_som,omega_som):
    som = MiniSom(16,16,leninput,sigma=omega_som,learning_rate=alpha_som)
    som.random_weights_init(data)
    print("Training...")
    som.train_batch(data,20000) # training with 10000 iterations
    print("\n...ready!")
    
    numpy.save('weight_som',som.weights)
   
    bone()
    pcolor(som.distance_map().T) # distance map as background
    colorbar()
    
    t = zeros(lentarget,dtype=int)
    
    # use different colors and markers for each label
    markers = ['o','s','D']
    colors = ['r','g','b']
    outfile = open('cluster-result.csv','w')
    for cnt,xx in enumerate(data):
        w = som.winner(xx) # getting the winner
        
        
        for z in xx:
            outfile.write("%s " % str(z))
        outfile.write("%s-%s \n" % (str(w[0]),str(w[1])))
        
        
    outfile.close()
 

def make_prefixSpan():
    pref_save = []
    print "Membuat Sequence Tanpa Prefixspan..."
    for row in db.cluster_result.find({"data_uji":no_uji}):
        sequence = row['topik'].split('|')
        if(len(sequence)<16):
            pref_save.append({"cluster":row['cluster'],"sequence":sequence,"min_sup":0,"data_uji":no_uji})
        else:
            new_sequence = []
            for i in range(0,15):
                new_sequence.append(sequence[i])
            pref_save.append({"cluster":row['cluster'],"sequence":new_sequence,"min_sup":0,"data_uji":no_uji})

    try:
        print "Menyimpan PrefixSpan..."
        db.prefix_result.insert_many(pref_save) 
        pref_save = []
        print "Berhasil Penyimpanan"
        pref_result.create_index([("cluster", pymongo.ASCENDING),("data_uji", pymongo.ASCENDING)])
        print "Berhasil Buat Index PrefixResult"
    except:
        print "Error Penyimpanan"


def populateDataClustered(cluster):
    clusters = db.cluster_result
    
    input_sequence = []
    for row in clusters.find({"cluster":cluster,"data_uji":no_uji}):
        input_sequence.append(row['topik'].split('|'))
    return input_sequence

def cek_pengujian_cluster_irisan():
    dat_cluster = pengujian.distinct("cluster")
    banyak_cluster = len(dat_cluster)
    precision = float(0)
    for clust in dat_cluster:
        precision_cluster = float(0)
        banyak_seq = pengujian.find({"cluster":clust}).count()
        for a in pengujian.find({"cluster":clust}):
            if(a["data_uji_count"]==0 and a["data_test_count"]==0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]>0 and a["data_test_count"]==0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]==0 and a["data_test_count"]>0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]>0 and a["data_test_count"]>0):
                precision_cluster += float(a["irisan"])/float(a["data_test_count"])
        if banyak_seq==0:
            banyak_cluster = banyak_cluster - 1
            #print "Zonk"
        else:
            precision = precision + (precision_cluster/float(banyak_seq))
            #print "Precision Cluster "+str(clust)+" = "+str(precision_cluster/banyak_seq)
        
    precision = precision / banyak_cluster
    return (precision*100)
    
'''
TRUE POSITIF = IRISAN NYA (ADA DI DUA2NYA)
FALSE POSITIF = ADA DI POLA BARU, TAPI GA ADA DI POLA YANG DIBUAT
FALSE NEGATIF = GA ADA DI POLA BARU, DI POLA YANG DIBUAT ADA
'''
def buat_pengujian(pengujian_no,param_uji):
    clusters = db.prefix_result
    print "Pengujian Berjalan, NO = " + str(pengujian_no)
    for m in range(16):
        for n in range(16):

            cluster_label = str(m)+"-"+str(n)
            
            print "Pengujian ke " + str(pengujian_no) + " pada Cluster " + str(cluster_label)

            seq = clusters.find({'cluster':cluster_label,'data_uji':0})
            jml_data_terbuat = seq.count()        
            if jml_data_terbuat > 0:
                '''
                Dari data Uji 0 di test atas data uji 1
                '''
                seq_list_uji = []
                for a_uji in seq:
                    joined_seq = "|".join(a_uji["sequence"])
                    seq_list_uji.append(joined_seq)                
                
                tp = float(0)
                fp = float(0)
                fn = float(0)
                seq_list_test = []                          
                i = 1
                seq_test = clusters.find({'cluster':cluster_label,'data_uji':i})
                jml_data_baru = seq_test.count()
                if jml_data_baru>0:
                    for b in seq_test:             
                        test_joined_seq = "|".join(b["sequence"])               
                        seq_list_test.append(test_joined_seq)                        
                        
                    for a in seq_list_test:
                        if(a in seq_list_uji):
                            tp = tp + 1
                        else:
                            fp = fp + 1

                    for a in seq_list_uji:
                        if(a not in seq_list_test):
                            fn = fn + 1

                    precision = float(0)
                    recall = float(0)
                    f1measure = float(0) 
                    if tp > 0:
                        precision = tp / (tp+fp)
                        recall = tp / (tp+fn)
                        f1measure = (2*precision*recall) / (precision+recall)                    

                    db.pengujian.insert({"pengujian_no":pengujian_no,"param_uji":param_uji,"cluster":cluster_label,"data_uji":i,"tp":tp,"fp":fp,"fn":fn,"precision":precision,"recall":recall,"f1measure":f1measure,"data_test_count":jml_data_terbuat,"data_uji_count":jml_data_baru})
                else:
                    fp = jml_data_terbuat
                    db.pengujian.insert({"pengujian_no":pengujian_no,"param_uji":param_uji,"cluster":cluster_label,"data_uji":i,"tp":0,"fp":fp,"fn":0,"precision":0,"recall":0,"f1measure":0,"data_test_count":jml_data_terbuat,"data_uji_count":jml_data_baru})

            else:
                i = 1
                seq_test = clusters.find({'cluster':cluster_label,'data_uji':i})
                jml_data_baru = seq_test.count()

                if jml_data_terbuat == 0 and jml_data_baru == 0:
                    continue
                else:
                    fn = jml_data_baru
                    db.pengujian.insert({"pengujian_no":pengujian_no,"param_uji":param_uji,"cluster":cluster_label,"data_uji":i,"tp":0,"fp":0,"fn":fn,"precision":0,"recall":0,"f1measure":0,"data_test_count":jml_data_terbuat,"data_uji_count":jml_data_baru})


def subPengujianBaruLoop():
    banyak_topik = 15
    param_SOM_Alpha = [0.1]
    param_SOM_Omega = [20,30,40,50]
    param_prefixSpan_minSup = [3,4,5]
    global no_uji      
    for alpha_som in param_SOM_Alpha:
        for omega_som in param_SOM_Omega:
            train_som(alpha_som, omega_som)                
            for i in range(4):
                no_uji = i
                test_som(alpha_som,omega_som)
                
            for min_sup in param_prefixSpan_minSup:
                for i in range(4):
                    no_uji = i
                    do_prefixSpan(min_sup)
                    
                buat_pengujian()
                presisi = cek_pengujian_cluster_irisan()  
                print "SELESAI PENGUJIAN, TINGKAT PRESISI = " + str(presisi)
                hasil_uji.insert({"banyak_topik":banyak_topik,"alpha_som":alpha_som,"omega_som":omega_som,"min_sup":min_sup,"presisi":presisi})
                
def onlyPrefixSpan():
    global no_uji
    banyak_topik = 15
    alpha_som = 0.5
    omega_som = 1
    param_prefixSpan_minSup = [3,4,5]
    pengujian = 2006
    for min_sup in param_prefixSpan_minSup:
        print "Dropping Prefix Result"
        db.prefix_result.drop()
        for i in range(1):
            no_uji = i
            do_prefixSpan(min_sup)
        no_uji = 1
        make_prefixSpan()
        buat_pengujian(pengujian,[banyak_topik,alpha_som,omega_som,min_sup])  

        pengujian = pengujian + 1

def gabungLog():
    for i in range(5):          
        no_uji = i
        cleanLog('server_log/log/access_log.'+str(i))

    file_gabung = open("server_log/log/gabung/access_log.0_clean","w")
    file_1 = open("server_log/log/access_log.0_clean","r")
    file_2 = open("server_log/log/access_log.1_clean","r")
    file_3 = open("server_log/log/access_log.2_clean","r")
    file_4 = open("server_log/log/access_log.3_clean","r")

    for line in file_1:
        file_gabung.write(line)

    for line in file_2:
        file_gabung.write(line)

    for line in file_3:
        file_gabung.write(line)

    for line in file_4:
        file_gabung.write(line)

def cobaSistem():
    global no_uji
    param_LDA = [10]
    param_SOM_Alpha = [0.5]
    param_SOM_Omega = [1]
    param_prefixSpan_minSup = [3]

    for banyak_topik in param_LDA:
        create_corpus(banyak_topik)  
        assign_topic()
        db.session_log.drop()
        for i in range(1):          
            no_uji = i
            sessionization('server_log/log/gabung/access_log.'+str(i)+'_clean')
        
        for alpha_som in param_SOM_Alpha:
            for omega_som in param_SOM_Omega:
                no_uji = 0
        
                train_som(alpha_som, omega_som)
                db.cluster_result.drop()
                for i in range(1):
                    no_uji = i
                    test_som(alpha_som,omega_som)
                    
                for min_sup in param_prefixSpan_minSup:
                    db.prefix_result.drop()
                    for i in range(1):
                        no_uji = i
                        do_prefixSpan(min_sup)

        
def pengujianBaruLoop():
    global no_uji
    param_LDA = [10,13,15,17,20,25,30,35]
    param_SOM_Alpha = [0.1,0.5,0.9]
    param_SOM_Omega = [1]
    param_prefixSpan_minSup = [2,3,4,5]
    pengujian = 3000

    pengujian_exist = db.pengujian.distinct("pengujian_no")

    for banyak_topik in param_LDA:
        if(pengujian not in pengujian_exist):
            create_corpus(banyak_topik)  
            assign_topic()
            print "Dropping Session History"
            db.session_log.drop()
            for i in range(2):          
                no_uji = i
                sessionization('server_log/log/gabung/access_log.'+str(i)+'_clean')
        
        for alpha_som in param_SOM_Alpha:
            for omega_som in param_SOM_Omega:
                no_uji = 0
                if(pengujian not in pengujian_exist):
                    train_som(alpha_som, omega_som)
                    print "Dropping Cluster Result"
                    db.cluster_result.drop()
                    for i in range(2):
                        no_uji = i
                        test_som(alpha_som,omega_som)
                    
                for min_sup in param_prefixSpan_minSup:
                    if(pengujian not in pengujian_exist):
                        print "Dropping Prefix Result"
                        db.prefix_result.drop()
                        for i in range(1):
                            no_uji = i
                            do_prefixSpan(min_sup)
                        no_uji = 1
                        make_prefixSpan()
                        buat_pengujian(pengujian,[banyak_topik,alpha_som,omega_som,min_sup])  

                    pengujian = pengujian + 1
                        
                    #presisi = cek_pengujian_cluster_irisan()  
                    #print "SELESAI PENGUJIAN, TINGKAT PRESISI = " + str(presisi)
                    #hasil_uji.insert({"banyak_topik":banyak_topik,"alpha_som":alpha_som,"omega_som":omega_som,"min_sup":min_sup,"presisi":presisi})
                    

'''    
param_LDA = [10,13,15]
param_SOM_Alpha = [0.1,0.5,0.9]
param_SOM_Omega = [1,10,20,30,40,50]
param_prefixSpan_minSup = [2,3,4]
'''

def summaryPengujian():
    outfile = open('precision.csv','w')
    outfile.write("Properties,Precision,Recall,F1Measure\n")
    for pengujian_no in range(9000,9015):
        i = 0
        sum_prec = 0
        sum_rec = 0
        sum_f1m = 0

        for p in db.pengujian.find({"pengujian_no":pengujian_no}):
            if p["precision"]==0:
                continue

            i = i + 1
            sum_prec = sum_prec + p["precision"]
            sum_rec = sum_rec + p["recall"]
            sum_f1m = sum_f1m + p["f1measure"]

            properties = p['param_uji']

        outfile.write(str(properties)+","+str(sum_prec/i)+","+str(sum_rec/i)+","+str(sum_f1m/i)+"\n")
        #print "Precision " + str(sum_prec/i)
        #print "Recall " + str(sum_rec/i)
        #print "F1Measure " + str(sum_f1m/i)
    outfile.close

#onlyPrefixSpan()

cobaSistem()
#buat_pengujian(1,[10,0.5,1,3])
#summaryPengujian()
