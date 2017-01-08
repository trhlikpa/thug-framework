import socket
from urlparse import urlparse


def hostname_to_ip(url):
    netloc = urlparse(url).netloc
    dom = netloc.split('@')[-1].split(':')[0]
    return socket.gethostbyname(dom)


def get_top_level_domain(url):
    netloc = urlparse(url).netloc
    return netloc.split('@')[-1].split(':')[0]
