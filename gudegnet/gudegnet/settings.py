# -*- coding: utf-8 -*-

# Scrapy settings for gudegnet project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'gudegnet'

SPIDER_MODULES = ['gudegnet.spiders']
NEWSPIDER_MODULE = 'gudegnet.spiders'
ITEM_PIPELINES = [
    'gudegnet.pipelines.MongoDBStorage',
]

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "gudegnet"
MONGODB_COLLECTION = "articles_news"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'gudegnet (+http://www.yourdomain.com)'
