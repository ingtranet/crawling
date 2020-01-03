# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class MongodbPipeline(object):
    def open_spider(self, spider):
        self.config = spider.mongo_config
        self.client = pymongo.MongoClient(self.config['host'])
        self.db = self.client[self.config['db']]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.config['collection']].replace_one({'_id': item['_id']}, item, upsert=True)
        return item
