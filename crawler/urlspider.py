from urlparse import urlparse
from scrapy import Spider, Request, http
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


def get_domain(url):
    netloc = urlparse(url).netloc
    return netloc.split('@')[-1].split(':')[0]


class UrlSpider(Spider):
    name = "url_spider"

    def __init__(self, data, callback, **kwargs):
        super(UrlSpider, self).__init__(**kwargs)
        self.callback = callback
        self.start_urls = [data['url']]
        self.custom_settings = dict(DEPTH_LIMIT=data['depth'])
        self._data = data
        if data['only_internal']:
            domain = get_domain(data['url'])
            self.allowed_domains = [domain]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                dont_filter=True,
                callback=self.parse,
            )

    def parse(self, response):
        for link in LxmlLinkExtractor(allow=(), deny=()).extract_links(response):
            yield http.Request(url=link.url, callback=self.callback, meta=self._data)
