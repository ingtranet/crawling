import os

import scrapy
from newspaper import Article

class DaumNewsSpider(scrapy.Spider):
    name = 'daum_news'
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawling.pipelines.MongodbPipeline': 100
        }
    }
    mongo_config = {
        'host': os.environ.get('MONGO_HOST', 'localhost:27017'),
        'db': 'crawling',
        'collection': 'daum_news'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.generate_url(self.code, 1, self.date),
            callback=self.parse_page, 
            meta={'code': self.code, 'page': 1, 'date': self.date})

    def parse_page(self, response):
        self.logger.info('Parsing URL: {}'.format(response.url))
        article_urls = response.css('.list_allnews .tit_thumb a.link_txt::attr("href")').extract()
        code = response.meta['code']
        page = response.meta['page']
        date = response.meta['date']

        if len(article_urls) and page <= 100:
            yield scrapy.Request(url=self.generate_url(code, page + 1, date),
                callback=self.parse_page, 
                meta={'code': code, 'page': page + 1, 'date': date})
                
        for url in article_urls:
            yield scrapy.Request(url=url,
                callback=self.parse_article,
                meta={'code': code, 'page': page + 1, 'date': date})

    
    def parse_article(self, response):
        self.logger.debug('Parsing URL: {}'.format(response.url))
        
        article = Article(response.url, language='ko')
        article.download(input_html=response.text)
        article.parse()

        result = {
            'code': response.meta['code'],
            'date': response.meta['date'],
            'title': article.title,
            'text': article.text,
            'publish_date': article.publish_date,
            'url': response.url
        } 
        result.update(self.parse_meta(article.meta_data))
        result['_id'] = result['url'].split('/')[-1]
        return result

    def parse_meta(self, meta):
        article = meta['article']
        return {
            'media_name': article['media_name'],
            'service_name': article['service_name']
        }

    def generate_url(self, media_code, page, reg_date):
        BASE_URL = 'https://media.daum.net/cp/{media_code}?page={page}&regDate={reg_date}'

        return BASE_URL.format(
            media_code=media_code,
            page=page,
            reg_date=reg_date)
        