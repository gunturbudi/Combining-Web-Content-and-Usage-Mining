import sys,datetime, pycountry,re,gensim,operator,numpy,pymongo
from wordcloud import WordCloud
from bottle import route, run, debug, template, static_file, view, url, request, os
from pymongo import MongoClient
from langdetect import detect
from pytz import country_names
from gensim import corpora, models, similarities
from numpy import *
from minisom import MiniSom
from pylab import plot,axis,show,pcolor,colorbar,bone
from bson.objectid import ObjectId
import matplotlib.pyplot as plt
import settings
from random import randint

ipDict = {}
session = {}
uniqueUrl = set()
noTopicUrl = set()
userAgentUnique = set()
rootUrl = settings.rootUrl
db = settings.db
articles = settings.articles
no_uji = 0


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@route('/app')
@view('wizard')
def wizard():
    return { 'get_url': url } 
    
@route('/check_article')
def check_article():
    count_article = articles.count()
    #print count_article
    return 'Found <strong>', str(count_article), '</strong> Content'

@route('/clean_article')
def clean_article():
    posts = db.articles
    article_concat = db.article_clean
    i = 0
    article_str = ""
    article_concat.remove({})
    for post in list(posts.find()):
        i = i+1
        article_str = " ".join(post['article_html'])
        article_str = article_str.strip()
        lang = "not_detected"
        try:
            lang = detect(article_str)
        except UnicodeDecodeError:
            lang = detect(article_str.decode("UTF-8"))
        except:
            print "Not Detected = ", article_str
        
        article_concat.insert({"url":post['url'],'article':article_str,'lang':lang,'topic':'-'});
        
    
    return 'Clean in <strong>',str(i),'</strong> Success!'

@route('/status_cleaned_article')
def status_cleaned_article():
    article_clean = articles
    str_lang = ""
    sizes= []
    labels = []
    for found_lang in article_clean.distinct('lang'):     
        #HARCODE   
        if found_lang=='id' or found_lang=='en':
            count_lang = article_clean.find({'lang':found_lang}).count()
            sizes.append((count_lang))
            if found_lang!='not_detected':
                '''
                I DONT KNOW WHY, JADI ERROR 
                KATANYA : KeyError alpha2

                ctry = pycountry.languages.get(alpha2=found_lang)
                labels.append(ctry.name)
                str_lang = str_lang + str(ctry.name) + ' : ' + str(count_lang)+'<br/> '

                DI HARCODE SAJA
                '''
                if(found_lang=='id'):
                    ctry_name = "Indonesia"
                elif(found_lang=="en"):
                    ctry_name = "English"

                labels.append(ctry_name)
                str_lang = str_lang + str(ctry_name) + ' : ' + str(count_lang)+'<br/> '
            else:
                str_lang = str_lang + "Not Detected " + ' : ' + str(count_lang)+'<br/> '
                labels.append("Not Detected")
            
    #str_lang = ','.join(lang_exist) 
    colors = ['yellowgreen', 'lightskyblue']
    explode = (0, 0.1) # only "explode" the 2nd slice (i.e. 'Hogs')
    print sizes
    print labels
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')    
    plt.savefig("static/count_article")
    
    str_return = 'Cleaned Article : <strong>',str(article_clean.count()),'</strong> <br/>Found = <br/> <strong>',str_lang,'</strong><br/>'
    str_return = str_return + "<img src='static/count_article.png' title='Count Article' />"

    return str_return

@route('/create_corpus')
@route('/create_corpus/<number_topic>')
def create_corpus(number_topic):
    
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


@route('/see_model')
@route('/see_model/<number_topic>/<lang>')
def see_model(number_topic,lang):
    file_model = ""
    if lang=="id":
        file_model = "lda/model_gudeg"
    elif lang=="en":
        file_model = "lda/model_gudeg_en"
    lda = gensim.models.LdaModel.load(file_model)
    model_str = "<table class='table'>"
    top_add = ""
    if(lang=="en"):
        top_add ="en"
    
    for i in range(int(number_topic)):
        topik_result = str(lda.print_topic(i))
        createWordCloud(topik_result,i)
        model_str = model_str + "<tr> <td><button type='button' onclick='showArticle(\""+(top_add+str(i))+"\")' class='btn btn-success'> Artikel Topik " + str(i+1) + " </button> </td><td><button type='button' onclick='showWordCloud(\""+(str(i))+"\")' class='btn btn-success'> Visualiasi Topik " + str(i+1) + " </button></td><td> " + topik_result + "</td></tr>"
        
    model_str = model_str + "</table>"
    
    
    
    return model_str

def createWordCloud(topik_result,topik_number):
    word_score = topik_result.split('+')
    freq = []
    for ws in word_score:
        tw = ws.split('*')
        freq.append((str(tw[1].strip()),float(tw[0].strip())))
    freq = tuple(freq)
    elements = WordCloud().generate_from_frequencies(freq)
    
    plt.imshow(elements)
    plt.axis("off")
    plt.savefig("static/lda/topik_"+str(topik_number))

@route('/get_article/<topic>')
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


@route('/get_wordcloud_visualisasi/<topic>')
def get_wordcloud_visualisasi(topic):
    html = "<img style='width: auto; height: auto;' src='/static/lda/topik_"+str(topic)+".png' />"
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

@route('/log_check')
def log_check():
    infile = open('server_log/server_log', "r")
    recordsRead = 0
    html = '<div role="alert" class="alert alert-warning alert-dismissible fade in">'
    html = html + ' <button aria-label="Close" data-dismiss="alert" class="close" type="button"><span aria-hidden="true">Close</span></button>'
    html = html + '  <strong>Make Sure!</strong> Everything on its place</div>'
    
    html = html + "<table class='table'>"
    html = html + "<tr><th>Date</th><th>IP Address</th><th>User Agent</th><th>Request</th><th>Status Code</th></tr>"
    
    for line in infile:
        regresult = parseLog(line)
        print regresult
        if (line[0] == '#'):
            continue
        else:
            recordsRead += 1
            theDate,ipAddr, userAgent, accessUrl, statusCode = regresult['time'],regresult['host'], regresult['agent'], regresult['request'], regresult['status']
            html = html + "<tr><td>"+str(theDate)+"</td><td>"+str(ipAddr)+"</td><td>"+str(userAgent)+"</td><td>"+str(accessUrl)+"</td><td>"+str(statusCode)+"</td></tr>"
            
            if recordsRead == 5:
                break
            
    html = html + "</table>"
    return html

@route('/assign_topic')
def assign_topic():
    lda = gensim.models.LdaModel.load('lda/model_gudeg')    
    dicts = corpora.Dictionary.load_from_text('lda/gudegarticle_dict.txt')    
    for article in list(articles.find({'lang':'id'})):
        artic = re.sub(r'([^\s\w]|_)+', '', article['article'])
        result = lda[dicts.doc2bow(artic.lower().split())]
        maxs = 0
        topic_selected = 0
        #print result
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

def check_topic_article():
    
    return "Something"

@route('/upload_log', method='POST')
def do_upload():
    upload     = request.files.get('upload')
    upload.filename = "server_log"
    os.remove('server_log/server_log')
    upload.save('server_log/') # appends upload.filename automatically
    return 'Server Log File Uploaded!'

def processLog(infileName):
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
            regexp = re.compile(r'bingbot|spider|Baiduspider')
            if regexp.search(userAgent) is not None:
                continue
               
            newRequestTime = datetime.datetime.strptime(theDate, "%d/%b/%Y:%H:%M:%S")
            client = MongoClient('localhost', 27017)
            db = client.gudegnet
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
                    if newRequestTime - ipdipaua[1] >= sessionTimeout:
                        ipdipaua[0] += 1
                        sessionNumber+=1
                        session[sessionNumber] = [accessUrl]
                    else:
                        session[sessionNumber].append(accessUrl)
                    ipdipaua[1] = newRequestTime
            
    
    return recordsRead

def saveSessions():
    db.session_log.remove({"data_uji":no_uji})
    session_log_db = db.session_log
    for key,value in session.iteritems():        
        session_seq = []
        for val in value:
            session_seq.append(val)
        session_log_db.insert({"key":(key-1),"session":session_seq,"data_uji":no_uji})


@route('/sessionization')
def sessionization():
    processLog('server_log/server_log')
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

@route('/train_som')
def train_som():
    session_log_db = db.session_log
    allTopic = articles.distinct("topic")
    
    uniqueTopic = []
    for t in allTopic:
        uniqueTopic.append("Topik " + str(t).strip())
    
    lentopic = len(uniqueTopic)

    panjangSOM = session_log_db.find({"data_uji":no_uji}).count()
    lebarSOM = lentopic*lentopic + lentopic*2 + 1
    
    #somInput = zeros((panjangSOM,lebarSOM),dtype=int16)
    
    # HARDCODE !!!!! #
    # lebarSOM = 484

    
    somInput = []
    for s in session_log_db.find({"data_uji":no_uji}):
        matrixSOM = getPresedenceMatrix(convertSession(s["session"],uniqueTopic),uniqueTopic,1)
        somInput.append(matrixSOM)

        #for t in s["session"]:
        #    somInput[s["key"],uniqueTopic.index(t)] = 1

    numpy.matrix(somInput)
    SOM(somInput,lebarSOM,panjangSOM)
    
    return "Berhasil Melakukan Training SOM"

def SOM(data,leninput,lentarget):
    som = MiniSom(16,16,leninput,sigma=1.0,learning_rate=0.5)
    som.random_weights_init(data)
    print("Training...")
    som.train_batch(data,10000) # training with 10000 iterations
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
        #print cnt
        #print xx
        #print w
        
        for z in xx:
            outfile.write("%s " % str(z))
        outfile.write("%s-%s \n" % (str(w[0]),str(w[1])))
        
        #outfile.write("%s %s\n" % str(xx),str(w))
        # palce a marker on the winning position for the sample xx
        #plot(w[0]+.5,w[1]+.5,markers[t[cnt]],markerfacecolor='None',
        #     markeredgecolor=colors[t[cnt]],markersize=12,markeredgewidth=2)
    outfile.close()
    #axis([0,som.weights.shape[0],0,som.weights.shape[1]])
    #show() # show the figure

@route('/test_som')
def test_som():
    print "Clustering.."
    
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

    som = MiniSom(16,16,lentopic,sigma=1.0,learning_rate=0.5)
    som.weights = numpy.load('weight_som.npy')
    #print som.weights
    outfile = open('cluster-result.csv','w')
    seq_number = 0
    cluster_mongo = db.cluster_result
    cluster_mongo.remove({"data_uji":no_uji})
    for cnt,xx in enumerate(somInput):
        w = som.winner(xx) # getting the winner
        #print cnt
        #print xx
        #print w
        
        #for z in xx:
        #    outfile.write("%s " % str(z))
        outfile.write("%s " % str(("|".join(oriSess[seq_number]))))
        outfile.write("%s-%s \n" % (str(w[0]),str(w[1])))
        cluster_mongo.insert({"topik":"|".join(oriSess[seq_number]),"cluster":(str(w[0])+"-"+str(w[1])),"data_uji":no_uji})
        seq_number = seq_number + 1
        #outfile.write("%s %s\n" % str(xx),str(w))
        # palce a marker on the winning position for the sample xx
        #plot(w[0]+.5,w[1]+.5,markers[t[cnt]],markerfacecolor='None',
        #     markeredgecolor=colors[t[cnt]],markersize=12,markeredgewidth=2)
    outfile.close()
    #TopikCluster()
    
    return "Berhasil Melakukan Clustering"
    
def TopikCluster():
    cluster_mongo = db.cluster_result
    
    outfile = open('cluster-topik.csv','w') 
    
    allTopic = articles.distinct("topic")
    uniqueUrlList = []
    for t in allTopic:
        uniqueUrlList.append("Topik " + str(t).strip())
    
    #print uniqueUrlList
    cluster_result_file = open('cluster-result.csv',"r")
    cluster_mongo.remove({"data_uji":no_uji})
    for line in cluster_result_file:
        topik = []
        dat = line.split()
        cluster_win = dat[len(dat)-1]
        found_any = 0
        for i in range(0,len(dat)-2):            
            if str(dat[i].strip())=="1":
                found_any = 1
                topik.append(uniqueUrlList[i])
                outfile.write("%s|" % (uniqueUrlList[i]))
        if found_any==1:
            outfile.write("%s" % cluster_win)
            outfile.write("\n")
            cluster_mongo.insert({"topik":"|".join(topik),"cluster":cluster_win,"data_uji":no_uji})
            
    
    outfile.close()

@route('/see_som_map/<no_uji_opt>')
def see_som_map(no_uji_opt):
    clusters = db.cluster_result
    no_uji_opt = int(no_uji_opt)
    map_html = "<table border=1>"
    for i in range(16):
        map_html = map_html + "<tr>"
        for j in range(16):
            cluster_label = str(i)+"-"+str(j)
            count_cluster = clusters.find({'cluster':cluster_label,'data_uji':no_uji_opt}).count()
            print(cluster_label,count_cluster)
            if count_cluster > 0:
                map_html = map_html + "<td style='text-align:center;width:30px;height:30px'><a href='#' onclick=getSomResult('"+cluster_label+"','"+str(no_uji_opt)+"')>"+str(count_cluster)+"</a></td>"
            else:
                map_html = map_html + "<td style='text-align:center;width:30px;height:30px'>"+str(count_cluster)+"</td>"
        map_html = map_html + "</tr>"
    map_html = map_html+"</table>"
    return map_html

@route('/get_som_result/<cluster>/<no_uji_opt>')
def get_som_result(cluster,no_uji_opt):
    html_som = "<ol>"
    no_uji_opt = int(no_uji_opt)
    clusters = db.cluster_result
    for pref in clusters.find({"cluster":cluster,'data_uji':no_uji_opt}):
        html_som = html_som + ("<li>" + str(pref["topik"])+"</li>")
    
    html_som = html_som + "</ol>"
    return html_som
        
@route('/prefixspan')
def do_prefixSpan():
    clusters = db.cluster_result
    pref_result = db.prefix_result
    
    pref_result.remove({"data_uji":no_uji})
    print "PrefixSpan Running"
    cluster_d = clusters.find({"data_uji":no_uji}).distinct("cluster")
    for d in cluster_d:        
        input_sequence = populateDataClustered(d)
        Prefixspan(input_sequence, 3,str(d))
    
    return "Berhasil Melakukan Sequence Pattern Mining dengan PrefixSpan"

@route('/see_prefix_result')
@route('/see_prefix_result/<no_uji_opt>')
def see_prefix_result(no_uji_opt):
    print no_uji_opt
    clusters = db.prefix_result
    no_uji_opt = int(no_uji_opt)
    map_html = "<table border=1>"
    for i in range(16):
        map_html = map_html + "<tr>"
        for j in range(16):
            cluster_label = str(i)+"-"+str(j)
            print cluster_label
            count_cluster = clusters.find({'cluster':cluster_label,'data_uji':no_uji_opt}).count()
            print count_cluster
            if count_cluster > 0:
                map_html = map_html + "<td style='text-align:center;width:30px;height:30px'><a href='#' onclick=getPrefix('"+cluster_label+"','"+str(no_uji_opt)+"')>"+str(count_cluster)+"</a></td>"
            else:
                map_html = map_html + "<td style='text-align:center;width:30px;height:30px'>"+str(count_cluster)+"</td>"
        map_html = map_html + "</tr>"
    map_html = map_html+"</table>"
    return map_html

@route('/get_prefix_result/<cluster>/<no_uji_opt>')
def get_prefix_result(cluster,no_uji_opt):
    html_prefix = "<ol>"
    no_uji_opt = int(no_uji_opt)
    clusters = db.prefix_result
    for pref in clusters.find({"cluster":cluster,'data_uji':no_uji_opt}):        
        html_prefix = html_prefix + ("<li>" + (" > ".join(pref["sequence"]))+" (support:" + str(pref["min_sup"]) + ")</li>")
    
    html_prefix = html_prefix + "</ol>"
    return html_prefix

def getTestArticle(topic,title,parent_str,href_str,article_id):
    uji_profil = db.uji_profil
    html = """<div class='panel panel-default'>
    <div class='panel-heading' role='tab' id='headingOne'>
      <h4 class='panel-title'>
        <a role='button' data-toggle='collapse' data-parent='#"""+parent_str+"""' href='#"""+href_str+"""' aria-expanded='false' aria-controls='"""+href_str+"""'>
          """+title+"""
        </a>
      </h4>
    </div>
    <div id='"""+href_str+"""' class='panel-collapse collapse' role='tabpanel' aria-labelledby='headingOne'>
      <div class='panel-body'>""";

    if(article_id!=""):
        article = articles.find_one({"_id": ObjectId(article_id)})
        uji_profil.insert_one(article)
    elif(topic==""):
        db.rekomendasi.delete_many({})
        uji_profil.delete_many({})

        count_article = articles.find({}).count()
        article = articles.find({}).limit(-1).skip(randint(1,count_article)).next()
        uji_profil.insert_one(article)
    else:
        if(is_number(topic)):
            topic = int(topic)
        else:
            topic = str(topic)

        count_article = articles.find({"topic":topic}).count()
        article = articles.find({"topic":topic}).limit(-1).skip(randint(1,count_article)).next()
        html = html + "<button type='button' value='next_article' class='btn btn-success btn-rekomen' id='"+str(article['_id'])+"'>Read This Next</button><br/>"

    html = html + "<a target='_blank' class='btn btn-default btn-xs' href='"+article['url']+"'>Article Link</a><br/>"
    html = html + "<p>" + article["article"] + "</p>"
    html = html + "</div></div></div>"

    return html

def getTopikRekomendasi(current_seq,prefix_cluster):
    rekomendasi_db = db.rekomendasi
    topik_rekomendasi = ""
    
    if(len(current_seq) == 1):
        for seq in prefix_cluster:
            if current_seq[0] == seq["sequence"][0] and len(seq["sequence"]) > 1:
                topik_rekomendasi = seq["sequence"][1]
                if db.uji_profil.find({}).count() >  rekomendasi_db.find({}).count():
                    rekomendasi_db.insert_one({"topik_rekomendasi":topik_rekomendasi,"sequence":seq["sequence"],"min_sup":seq["min_sup"],"cluster":seq["cluster"]})
                break
    elif(len(current_seq)>1):
        join_seq = '|'.join(current_seq)
        len_curr_seq = len(current_seq)
        for seq in prefix_cluster:
            if len_curr_seq < len(seq["sequence"]):
                temp_cek_join = []
                for i  in range(0,len_curr_seq):
                    temp_cek_join.append(seq["sequence"][i])
                temp_cek_join = '|'.join(temp_cek_join)
                if join_seq == temp_cek_join:
                     topik_rekomendasi = seq["sequence"][len_curr_seq]
                     if db.uji_profil.find({}).count() >  rekomendasi_db.find({}).count():
                        rekomendasi_db.insert_one({"topik_rekomendasi":topik_rekomendasi,"sequence":seq["sequence"],"min_sup":seq["min_sup"],"cluster":seq["cluster"]})
                     break

    return topik_rekomendasi

@route('/test_random_article')
def test_random_article():
    html = getTestArticle("","Random Article",'accordion_article','col1',"")

    return html

@route('/test_recommendation')
def test_recommendation():
    uji_profil = db.uji_profil
    current_seq = []
    for t in uji_profil.find({}):
        current_seq.append("Topik " + str(t['topic']))

    '''
    APPLY SOM
    '''
    allTopic = articles.distinct("topic")
    lentopic = len(allTopic)
    uniqueTopic = []
    for t in allTopic:
        uniqueTopic.append("Topik " + str(t).strip())

    lebarSOM = lentopic*lentopic + lentopic*2 + 1
    
    somInput = []
    somInput.append(getPresedenceMatrix(convertSession(current_seq,uniqueTopic),uniqueTopic,1))
    som = MiniSom(16,16,lentopic,sigma=1.0,learning_rate=0.5)
    som.weights = numpy.load('weight_som.npy')
    cluster_winner = ""
    for cnt,xx in enumerate(somInput):
        w = som.winner(xx) # getting the winner
        cluster_winner = (str(w[0])+"-"+str(w[1]))

    '''
    SEARCH FOR THE PATTERN IN PARTICULAR CLUSTER
    '''

    print cluster_winner
    print current_seq

    prefix_result = db.prefix_result
    prefix_cluster = prefix_result.find({"cluster":cluster_winner,"data_uji":no_uji}).sort("min_sup",pymongo.DESCENDING)

    topik_rekomendasi = getTopikRekomendasi(current_seq,prefix_cluster)

    if topik_rekomendasi == "":
        prefix_cluster = prefix_result.find({"data_uji":no_uji}).sort("min_sup",pymongo.DESCENDING)
        topik_rekomendasi = getTopikRekomendasi(current_seq,prefix_cluster)
    
    html = "--tidak ada topik rekomendasi--"
    if(topik_rekomendasi!=""):
        the_topik = topik_rekomendasi.replace("Topik","").strip()
        html = getTestArticle(the_topik,"Rekomendasi 1","accordion_recommendation",'col_rek1',"")
        html += getTestArticle(the_topik,"Rekomendasi 2","accordion_recommendation",'col_rek2',"")
        html += getTestArticle(the_topik,"Rekomendasi 3","accordion_recommendation",'col_rek3',"")

    return html

@route('/get_next_read/<article_id>')
def get_next_read(article_id):
    html = getTestArticle("","Next Article",'accordion_article','col1',article_id)

    return html

def getAccordExplain(title,href_str,content):
    html = """<div class='panel panel-default'>
    <div class='panel-heading' role='tab' id='headingOne'>
      <h4 class='panel-title'>
        <a role='button' data-toggle='collapse' data-parent='#accordion_recommendation' href='#"""+href_str+"""' aria-expanded='false' aria-controls='"""+href_str+"""'>
          """+title+"""
        </a>
      </h4>
    </div>
    <div id='"""+href_str+"""' class='panel-collapse collapse' role='tabpanel' aria-labelledby='headingOne'>
      <div class='panel-body'>""";

    html = html + content
    html = html + "</div></div></div>"

    return html


@route('/explain_recommendation')
def explain_recommendation():
    rekomendasi_db = db.rekomendasi
    uji_profil = db.uji_profil

    uji_profil_data =  uji_profil.find({})
    rekomendasi_data = rekomendasi_db.find({})
    print uji_profil_data.count()
    print rekomendasi_data.count()
    html = ""
    i = 1
    for p in uji_profil_data:
        content = "<table class='table'>"
        content = content + "<tr><th>Topik</th><td>Topik "+str(p['topic'])+"</td></tr>"
        content = content + "<tr><th>Visualiasi</th><td><button type='button' onclick='showWordCloud(\""+str(p['topic'])+"\")' class='btn btn-success'> Visualiasi Topik " + str(i+1) + " </button></td>"
        content = content + "<tr><th>Artikel</th><td>"+p['article']+"</td></tr>"
        content = content + "</table>"

        html = html + getAccordExplain("Article #"+str(i),"article_"+str(i),content)

        try:
            content = "<table class='table'>"
            content = content + "<tr><th>Cluster</th><td><a href='#' onclick=getPrefix('"+rekomendasi_data[i-1]["cluster"]+"','"+str(no_uji)+"')>"+rekomendasi_data[i-1]["cluster"]+"</a>"+"</td></tr>"
            content = content + "<tr><th>Sequence</th><td>"+ " > ".join(rekomendasi_data[i-1]["sequence"])+"</td></tr>"
            content = content + "<tr><th>Minimum Support</th><td>"+str(rekomendasi_data[i-1]["min_sup"])+"</td></tr>"
            content = content + "<tr><th>Rekomendasi</th><td>"+rekomendasi_data[i-1]["topik_rekomendasi"]+"</td></tr>"
            content = content + "</table>"

            html = html + getAccordExplain("Rekomendasi #"+str(i),"rekomendasi_"+str(i),content)
        except Exception:
            continue

        i = i+1

    return html

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def populateDataClustered(cluster):
    clusters = db.cluster_result
    
    input_sequence = []
    for row in clusters.find({"cluster":cluster,"data_uji":no_uji}):
        input_sequence.append(row['topik'].split('|'))
    return input_sequence

class Prefixspan:
    def __init__(self, S, supp, file_output):
        self.S = S
        self.supp = supp
        self.seq_pats = []
        self.freq = self.prefixspan([], 0, self.S)
        self.saveFinalResult(file_output,self.seq_pats)
        #print 'list of frequent sequences: ' + str(self.seq_pats)
        
    def saveFinalResult(self,file_output,seq_pat):
        client = MongoClient('localhost', 27017)
        db = client.gudegnet
        pref_result = db.prefix_result
        
        outfile = open('final_result/cluster_'+file_output, "w")
        for pat in self.seq_pats:
            outfile.write("%s\n" % str(pat))
            pref_result.insert({"cluster":file_output,"sequence":pat[0],"min_sup":pat[1],"data_uji":no_uji})
            #if len(pat[0]) > 1:
            #    pref_result.insert({"cluster":file_output,"sequence":pat[0],"min_sup":pat[1]})
        outfile.close()
        
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
    

debug(True)
run(reloader=True)