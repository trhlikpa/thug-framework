from scrapy import Spider, Request, http
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from worker.utils.netutils import get_top_level_domain


class UrlSpider(Spider):
    """
    Spider that extracts only links to the specified depth
    """
    name = "url_spider"

    def __init__(self, url, callback, only_internal=True, allowed_domains=None):
        """
        Spider constructor
        :param url: start url
        :param callback: spider runs callback for every link
        :param only_internal: crawl only initial domain
        :param allowed_domains: list of allowed domains
        """
        self.callback = callback
        self.start_urls = [url]

        if only_internal:
            domain = get_top_level_domain(url)
            self.allowed_domains = [domain]
        elif allowed_domains is not None and len(allowed_domains) > 0:
            self.allowed_domains = allowed_domains

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
            yield http.Request(url=link.url, callback=self.callback)
