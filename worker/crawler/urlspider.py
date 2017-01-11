from scrapy import Item, Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class UrlItem(Item):
    url = Field()


class UrlSpider(CrawlSpider):
    name = 'url_spider'
    allowed_domains = []
    start_urls = []
    callback = None

    rules = (Rule(LinkExtractor(allow=()), callback='parse_link', follow=True),)

    def __init__(self, url, allowed_domains, callback, *args, **kwargs):
        self.start_urls = [url]
        self.allowed_domains = allowed_domains
        self.callback = callback
        super(UrlSpider, self).__init__(*args, **kwargs)

    def parse_link(self, response):
        item = UrlItem()
        item['url'] = response.url

        self.callback(response)

        return item
