import io
import json
import os
from celery import Celery
from pymongo import MongoClient

__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)


@celery.task(bind='true', time_limit=3600)
def crawl_urls(self, data):

    from scrapy.crawler import CrawlerProcess
    from crawler.urlspider import UrlSpider

    db_client = MongoClient(config['MONGODB_URL'])
    db = db_client.thug_database

    process = CrawlerProcess({
        'USER_AGENT': config['CRAWLER_USER_AGENT'],
        'DOWNLOAD_DELAY': config['CRAWLER_DOWNLOAD_DELAY']
    })

    try:
        process.crawl(UrlSpider, data=data, callback=crawler_callback)
        process.start()
    except Exception as error:
        print error.message
    finally:
        db_client.close()


def crawler_callback(request):
    from worker.tasks import analyze_url

    data = request.meta
    data['url'] = request.url
    analyze_url.apply_async(args=[data])


def print_this_link(request):
    print('link: {}'.format(request.url))
