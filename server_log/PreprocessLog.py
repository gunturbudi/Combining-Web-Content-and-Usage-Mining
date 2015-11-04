import datetime,re,operator,sys,random,numpy
from numpy import *
from pymongo import MongoClient
from minisom import MiniSom
from pylab import plot,axis,show,pcolor,colorbar,bone


client = MongoClient('localhost', 27017)
db = client.gudegnet
articles = db.article_directory
cluster_mongo = db.cluster_result


infileName = "access_log"
outfileName = "visitor-ips-no-topic.csv"
rootUrl = "https://www.gudeg.net"

ipDict = {}
session = {}
uniqueUrl = set()
noTopicUrl = set()

userAgentUnique = set()

def inputRecords():
    infile = open(infileName, "r")

    recordsRead = 0
    sessionNumber = 0
    progressThreshold = 100
    sessionTimeout = datetime.timedelta(minutes=30)
    
    for line in infile:
        
        if (line[0] == '#'):
            continue
        else:
            recordsRead += 1

            fields = line.split()
            
            #if recordsRead == 1000:
            #    break            
            
            if (recordsRead >= progressThreshold):
                print "Read %d records" % recordsRead
                progressThreshold *= 2

            theDate = fields[3]
            ipAddr, userAgent, accessUrl, statusCode = fields[0], fields[-1], fields[6], fields[8]
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
            regexp = re.compile(r'bingbot|spider')
            if regexp.search(userAgent) is not None:
                continue
               
            newRequestTime = datetime.datetime.strptime(theDate, "[%d/%b/%Y:%H:%M:%S")
            
            topic = articles.find_one({"url":rootUrl+accessUrl},{"topic":1})
            if topic is not None:
                accessUrl = "Topik "+str(topic['topic'])
            else:                
                noTopicUrl.add(accessUrl)
                continue
                randomTopic = random.randint(1,14)   
                accessUrl = "Topik " + str(randomTopic)
            
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

def outputSessions():
    uniqueUrlList = list(uniqueUrl)
    outfile = open('unik_url.csv', "w")
    for ur in uniqueUrlList:
        outfile.write("%s\n" % (ur))
    outfile.close()
    
    somInput = zeros((len(session),len(uniqueUrlList)),dtype=int16)
    
    outfile = open(outfileName, "w")
    for key,value in session.iteritems():        
        outfile.write("%s\n" % (value))
        for val in value:
            somInput[key-1,uniqueUrlList.index(val)] = 1
    SOM(somInput,len(uniqueUrlList),len(session))
    TopikCluster()
    outfile = open('total-visitor.csv', "w")
    recordsWritten = len(ipDict)
    for ip, val in ipDict.iteritems():
        totalSessions = reduce(operator.add, [v2[0] for v2 in val.itervalues()])
        outfile.write("%s\t%d\n" % (ip, totalSessions))
        
    outfile.close()
    return recordsWritten

def TopikCluster():
    outfile = open('cluster-topik.csv','w') 
    
    uniqueUrlList = []
    unik_url_file = open('unik_url.csv', "r")
    for line in unik_url_file:
        uniqueUrlList.append(line.strip())
    
    #print uniqueUrlList
    cluster_result_file = open('cluster-result.csv',"r")
    cluster_mongo.remove({})
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
            cluster_mongo.insert({"topik":"|".join(topik),"cluster":cluster_win})
            
    
    outfile.close()

def SOM(data,leninput,lentarget):
    som = MiniSom(5,5,leninput,sigma=1.0,learning_rate=0.5)
    som.random_weights_init(data)
    print("Training...")
    som.train_batch(data,10000) # training with 10000 iterations
    print("\n...ready!")
    
    numpy.save('weight_som.txt',som.weights)
   
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
    

recordsRead = inputRecords()

recordsWritten = outputSessions()

print "Finished session reconstruction: read %d records, wrote %d\n" % (recordsRead, recordsWritten)
print "No Topic URL "+str(len(noTopicUrl))

outfile = open('no-topic-url.csv','w')
for url in noTopicUrl:
    outfile.write("%s\n" % url)
    
outfile = open('user-agent.csv','w')
for agent in userAgentUnique:
    outfile.write("%s\n" % agent)