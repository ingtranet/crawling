import os
import time
from datetime import datetime
from shutil import which
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class NaverBlogSpider(scrapy.Spider):
    name = 'naver_blog'
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawling.pipelines.MongodbPipeline': 100
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 100
        }
    }
    mongo_config = {
        'host': os.environ.get('MONGO_HOST', 'localhost:27017'),
        'db': 'crawling',
        'collection': 'naver_blog'
    }

    def start_requests(self):
        yield SeleniumRequest(url=self.generate_url(1),
            wait_time=5,
            wait_until=EC.presence_of_element_located((By.CLASS_NAME, "info_post")),
            callback=self.parse_page, 
            meta={'page': 1})

    def parse_page(self, response):
        article_urls = response.css('a.desc_inner::attr("href")').extract()
        page = response.meta['page']

        if len(article_urls) and page <= 100:
            yield SeleniumRequest(url=self.generate_url(page + 1),
                wait_time=5,
                wait_until=EC.presence_of_element_located((By.CLASS_NAME, "info_post")),
                callback=self.parse_page, 
                meta={'page': page + 1})
                
        for url in article_urls:
            yield scrapy.Request(url=url, callback=self.parse_article)

    
    def parse_article(self, response):
        if response.css('#mainFrame'):
            path = response.css('#mainFrame::attr("src")').get()
            return scrapy.Request(url=urljoin('https://blog.naver.com', path), callback=self.parse_article)
        
        result = {
            '_id': response.css('meta[property="og:url"]::attr("content")').get(),
            'crawled_at': datetime.utcnow(),
            'title': response.css('meta[property="og:title"]::attr("content")').get(),
            'content': response.css('div.se-main-container').get(),
            'url': response.url
        }
        return result

    def generate_url(self, page):
        BASE_URL = 'https://section.blog.naver.com/BlogHome.nhn?directoryNo=0&currentPage={page}&groupId=0'

        return BASE_URL.format(page=page)
        