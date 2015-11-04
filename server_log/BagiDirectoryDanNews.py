from pymongo import MongoClient

client = MongoClient('localhost',27017)
db = client.gudegnet
articles_left = db.article_left_clean1
articles_clean = db.article_clean

article_directory = db.article_directory
article_news = db.article_news


for article in articles_left.find({"url":{"$regex":u"directory"}}):
    article_directory.insert({"url":article['url'],'article':article['article'],'lang':article['lang'],'topic':'-'})
    
for article in articles_left.find({"url":{"$regex":u"news"}}):
    article_news.insert({"url":article['url'],'article':article['article'],'lang':article['lang'],'topic':'-'})


for article in articles_clean.find({"url":{"$regex":u"directory"}}):
    article_directory.insert({"url":article['url'],'article':article['article'],'lang':article['lang'],'topic':'-'})

