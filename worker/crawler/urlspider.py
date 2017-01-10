from scrapy import http
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class UrlSpider(CrawlSpider):
    name = 'url_spider'
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com']
    callback = None

    rules = (Rule(LinkExtractor(allow=()), callback='parse_obj', follow=True),)

    def __init__(self, url, allowed_domains, callback, *args, **kwargs):
        super(UrlSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.allowed_domains = allowed_domains
        self.callback = callback

    def parse_obj(self, response):
        for link in LinkExtractor(allow=(), deny=self.allowed_domains).extract_links(response):
            yield http.Request(url=link.url, callback=self.callback)
