import io
import json
import os
from uuid import uuid4
from celery import Celery
from pymongo import MongoClient

# Load config.json file
__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)


@celery.task(bind='true', time_limit=3600)
def crawl_urls(self, input_data):
    """
    Celery method that uses specified spider to recursively crawl urls
    :param self: Task object self reference
    :param input_data: Dictionary with data for spider
    """

    # Lazy load of task dependencies
    from scrapy.crawler import CrawlerProcess
    from crawler.urlspider import UrlSpider

    db_client = MongoClient(config['MONGODB_URL'])
    db = db_client.thug_database

    process = CrawlerProcess({
        'USER_AGENT': config['CRAWLER_USER_AGENT'],
        'DOWNLOAD_DELAY': config['CRAWLER_DOWNLOAD_DELAY']
    })

    db.jobs.update_one({'_id': self.request.id}, {'$set': {'_state': 'STARTED'}}, upsert=True)

    def _crawler_callback(link):
        """
        Callback function that spider executes for every link
        :param link: input link
        """
        from worker.tasks import analyze_url

        data = link.meta
        data['url'] = link.url

        uuid = str(uuid4())

        json_data = {
            '_id': uuid,
            'url': link.url,
            '_state': 'PENDING'
        }

        db.tasks.insert(json_data)
        db.jobs.update_one({'_id': self.request.id}, {'$push': {'tasks': uuid}}, upsert=True)
        analyze_url.apply_async(args=[data], task_id=uuid)

    try:
        process.crawl(UrlSpider, data=input_data, callback=_crawler_callback)
        process.start(True)

        db.jobs.update_one({'_id': self.request.id}, {'$set': {'_state': 'SUCCESS'}}, upsert=True)
    except Exception as error:
        db.jobs.update_one({'_id': self.request.id}, {'$set': {'_state': 'FAILURE', 'error': error.message}},
                           upsert=True)
    finally:
        db_client.close()
