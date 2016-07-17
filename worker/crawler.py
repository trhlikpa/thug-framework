from urlparse import urlparse
from scrapy import Spider, Request, http
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


def print_this_link(link):
    print "Link --> {this_link}".format(this_link=link)


def get_domain(url):
    netloc = urlparse(url).netloc
    return netloc.split('@')[-1].split(':')[0]


class UrlSpider(Spider):
    name = "url_spider"

    def __init__(self, url, depth, only_internal=False, **kwargs):
        super(UrlSpider, self).__init__(**kwargs)
        self.start_urls = [url]
        self.custom_settings = dict(DEPTH_LIMIT=depth)
        if only_internal:
            domain = get_domain(url)
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
            yield http.Request(url=link.url, callback=print_this_link)
