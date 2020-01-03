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
        'host': 'localhost:27017',
        'db': 'default',
        'collection': 'iamhappy'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.generate_url(1),
            callback=self.parse_page, 
            meta={'page': 1})

    def parse_page(self, response):
        self.logger.debug('Parsing URL: {}'.format(response.url))
        article_urls = response.css('.list_allnews .tit_thumb a.link_txt::attr("href")').extract()
        page = response.meta['page']

        if len(article_urls) and page <= 100:
            yield scrapy.Request(url=self.generate_url(page + 1),
                callback=self.parse_page, 
                meta={'page': page + 1})
                
        for url in article_urls:
            yield scrapy.Request(url=url, callback=self.parse_article)

    
    def parse_article(self, response):
        self.logger.debug('Parsing URL: {}'.format(response.url))
        
        article = Article(response.url, language='ko')
        article.download(input_html=response.text)
        article.parse()

        result = {
            'title': article.title,
            'text': article.text,
            'publish_date': article.publish_date,
            'url': response.url,
            'body': response.body
        } 
        result.update(self.parse_meta(article.meta_data))
        result['_id'] = result['url']
        yield result

    def parse_meta(self, meta):
        article = meta['article']
        return {
            'url': article['txid'],
            'media_name': article['media_name'],
            'service_name': article['service_name']
        }

    def generate_url(self, page):
        BASE_URL = 'https://media.daum.net/cp/{media_code}?page={page}&regDate={reg_date}'

        return BASE_URL.format(
            media_code=self.media_code,
            page=page,
            reg_date=self.reg_date)
        