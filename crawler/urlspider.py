from urlparse import urlparse
from scrapy import Spider, Request, http
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


def get_domain(url):
    """
    Function retuns domain name of url
    :param url: input url
    :return: domain name
    """
    netloc = urlparse(url).netloc
    return netloc.split('@')[-1].split(':')[0]


class UrlSpider (Spider):
    """
    Spider that extracts only links into the specified depth
    """
    name = "url_spider"

    def __init__(self, data, callback, **kwargs):
        """
        Spider ctor
        :param data: depth | url | only_internal parameters
        :param callback: spider runs callback for every link
        """
        super(UrlSpider, self).__init__(**kwargs)
        self.callback = callback
        self.start_urls = [data['url']]
        self.custom_settings = dict(DEPTH_LIMIT=data['depth'])
        self._data = data
        if data['only_internal'] == 'True':
            domain = get_domain(data['url'])
            self.allowed_domains = [domain]

    def start_requests(self):
        """
`       Method is called only once by crawler when the spider is opened
        Safe to implement as generator
        :return: Iterable with http request
        """
        for url in self.start_urls:
            yield Request(
                url,
                dont_filter=True,
                callback=self.parse,
            )

    def parse(self, response):
        """
        Parses links from DOM and calls callback on every link
        :param response: response to parse
        """
        for link in LxmlLinkExtractor(allow=(), deny=()).extract_links(response):
            yield http.Request(url=link.url, callback=self.callback, meta=self._data)
