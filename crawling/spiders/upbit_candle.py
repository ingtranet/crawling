import os
import time
import json
from datetime import datetime
from shutil import which
from urllib.parse import urljoin, urlparse

import pymongo
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class UpbitCandleSpider(scrapy.Spider):
    name = 'upbit_candle'
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawling.pipelines.MongodbPipeline': 100
        }
    }

    mongo_config = {
        'host': os.environ.get('MONGO_HOST', 'localhost:27017'),
        'db': 'crawling',
        'collection': 'upbit_candle'
    }

    def start_requests(self):
        if hasattr(self, 'datetime'):
            yield scrapy.Request(
                url=self.generate_url(self.market, self.datetime.split('+')[0].replace('T', ' ')),
                callback=self.parse_result)
        else:
            client = pymongo.MongoClient(self.mongo_config['host'])
            db = client[self.mongo_config['db']]
            collection = db[self.mongo_config['collection']]
            self.latest = collection.find_one({'market': self.market}, sort=[('candle_date_time_utc', pymongo.DESCENDING)])
            if not self.latest:
                self.latest = {'candle_date_time_utc': '1970-01-01T00:00:00'}
        
            yield scrapy.Request(
                url=self.generate_url(self.market, ''),
                callback=self.parse_result)

    def parse_result(self, response):
        response = json.loads(response.text)
        for item in response:
            item['_id'] = f"{item['market']}_{item['candle_date_time_utc']}"
            item['candle_date_time'] = datetime.strptime(item['candle_date_time_utc'], '%Y-%m-%dT%H:%M:%S')
            yield item

        if not hasattr(self, 'datetime'):
            if len(response) != 0:
                smallest_dt = min([item['candle_date_time_utc'] for item in response])
                if smallest_dt > self.latest['candle_date_time_utc']:
                    yield scrapy.Request(
                        url=self.generate_url(self.market, smallest_dt.replace('T', ' ')),
                        callback=self.parse_result)

    def generate_url(self, market, to):
        BASE_URL = 'https://api.upbit.com/v1/candles/minutes/1?count=200&market={market}&to={to}'

        return BASE_URL.format(market=market, to=to)
        