from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.gudegnet
articles = db.article_directory
rootUrl = "https://www.gudeg.net"