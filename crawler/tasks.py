import io
import json
import os
from uuid import uuid4

from celery import Celery
from pymongo import MongoClient

__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)


@celery.task(bind='true', time_limit=3600)
def crawl_urls(self, input_data):
    from scrapy.crawler import CrawlerProcess
    from crawler.urlspider import UrlSpider

    db_client = MongoClient(config['MONGODB_URL'])
    db = db_client.thug_database

    process = CrawlerProcess({
        'USER_AGENT': config['CRAWLER_USER_AGENT'],
        'DOWNLOAD_DELAY': config['CRAWLER_DOWNLOAD_DELAY']
    })

    db.jobs.update({'_id': self.request.id}, dict(_state='STARTED'), True)

    def _crawler_callback(link):
        from worker.tasks import analyze_url

        data = link.meta
        data['url'] = link.url

        uuid = str(uuid4())

        json_data = {
            '_id': uuid,
            '_state': 'PENDING'
        }

        db.tasks.insert(json_data)
        db.jobs.update_one({'_id': str(self.request.id)}, {'$push': {'tasks': uuid}}, True)
        analyze_url.apply_async(args=[data], task_id=uuid)

    try:
        process.crawl(UrlSpider, data=input_data, callback=_crawler_callback)
        process.start()
        db.jobs.update({'_id': self.request.id}, {'$set': {'_state': 'SUCCESS'}}, True)
    except Exception as error:
        db.jobs.update({'_id': self.request.id}, {'$set': {'_state': 'FAILURE', 'error': error.message}}, True)
    finally:

        db_client.close()
