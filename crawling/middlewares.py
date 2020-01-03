# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


from scrapy import signals
import pymongo

class MongodbMiddleware(object):
    def __init__(self):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.config = spider.mongo_config
        self.client = pymongo.MongoClient(self.config['host'])
        self.db = self.client[self.config['db']]

    def spider_closed(self, spider):
        self.client.close()

    def process_response(self, request, response, spider):
        if response.status == 200:
            data = {'_id': response.url, 'body': response.body}
            self.db['raw'].replace_one({'_id': response.url}, data, upsert=True)
        return response


