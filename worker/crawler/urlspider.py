from scrapy import Item, Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class UrlItem(Item):
    """
    Represents single url
    """
    url = Field()


class UrlSpider(CrawlSpider):
    """
    Spider that only collects urls
    """
    name = 'url_spider'
    allowed_domains = []
    start_urls = []
    callback = None

    rules = (Rule(LinkExtractor(allow=()), callback='parse_link', follow=True),)

    def __init__(self, url, allowed_domains, callback, *args, **kwargs):
        """
        :param url: initial url
        :param allowed_domains: list of allowed domains
        :param callback: callback function
        :param args: arguments
        :param kwargs: key word arguments
        """
        self.start_urls = [url]
        self.allowed_domains = allowed_domains
        self.callback = callback
        super(UrlSpider, self).__init__(*args, **kwargs)

    def parse_link(self, response):
        """
        Executes callback on every parsed url
        :param response: scrapy response object
        :return: UrlItem
        """
        item = UrlItem()
        item['url'] = response.url

        self.callback(response)

        return item
