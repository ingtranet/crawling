# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.exceptions import CloseSpider

class MongodbPipeline(object):
    def open_spider(self, spider):
        self.config = spider.mongo_config
        self.client = pymongo.MongoClient(self.config['host'])
        self.db = self.client[self.config['db']]
        self.collection = self.db[self.config['collection']]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.collection.replace_one({'_id': item['_id']}, item, upsert=True)
        except Exception as e:
            spider.crawler.stop()
            raise e
        return item
