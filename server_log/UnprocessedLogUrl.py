from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep # be nice
from HTMLParser import HTMLParser
import lxml,re
from lxml.html.clean import Cleaner
from langdetect import detect
from pymongo import MongoClient
from boto.s3.multipart import Part

cleaner = Cleaner()
cleaner.javascript = True # This is True because we want to activate the javascript filter
cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

BASE_URL = "https://gudeg.net"
 
def make_soup(url):
    html = ""
    try:
        html = urlopen(url).read()
    except Exception, e:
        print e
        
    return BeautifulSoup(html, "lxml")
 
def get_article(url):
    soup = make_soup(url)
    #print soup
    data = soup.find("div", "konten-data")
    #print lxml.html.tostring(cleaner.clean_html(data))
    #print data
    return strip_tags(str(data))

def get_article_news(url):
    soup = make_soup(url)
    #print soup
    data = soup.find("div", {"id":"dbody"})
    
    return strip_tags(str(data))

def get_lang(article_str):
    lang = "not_detected"
    try:
        lang = detect(article_str)
    except UnicodeDecodeError:
        lang = detect(article_str.decode("UTF-8"))
    except:
        "Not Detected = " + article_str
    return lang

client = MongoClient('localhost', 27017)
db = client.gudegnet
articles = db.article_left
article_no_content = db.article_no_content
for part_log in range(96,100):
    print "Start Part Log " + str(part_log) + "\n"
    file_txt = "notopic/no-topic-urlPart" + str(part_log) + ".txt"
    infile = open(file_txt, "r")
    recordsRead = 0
    progressThreshold = 1
    for line in infile:
        article_url = BASE_URL+line
        recordsRead += 1
        
        
        if (recordsRead >= progressThreshold):
            print "Read %d records" % recordsRead
            progressThreshold *= 2
            
        urlExist = articles.find_one({"url":article_url})
        if urlExist is not None:
            continue
    
        article_content = None
        regexp = re.compile(r'directory')
        if regexp.search(line) is not None:
            try: 
                article_content = get_article(article_url)   
            except Exception, e:
                print e     
            
        regexp = re.compile(r'news')
        if regexp.search(line) is not None:
            try:                
                article_content = get_article_news(article_url)
            except Exception, e:
                print e
        
        if article_content is not None:
            lang = "-"
            try:
                lang = get_lang(article_content)
            except Exception, e:
                print e
            
            articles.insert({"url":article_url,'article':article_content,'lang':lang,'topic':'-','part':part_log})
        else:
            print article_url
            article_no_content.insert({"url":article_url,'part':part_log})