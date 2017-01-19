from socket import gethostbyname
from urlparse import urlparse
from httplib import HTTPConnection

from worker.utils.exceptions import UrlFormatError


def url_to_ip(url):
    netloc = urlparse(url).netloc
    dom = netloc.split('@')[-1].split(':')[0]
    ip = gethostbyname(dom)

    if ip == '0.0.0.0':
        raise UrlFormatError

    return ip


def get_top_level_domain(url):
    netloc = urlparse(url).netloc
    domain = netloc.split('@')[-1].split(':')[0]

    if not domain:
        raise UrlFormatError

    return domain


def check_url(url):
    p = urlparse(url)
    conn = HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()

    return resp.status < 400
