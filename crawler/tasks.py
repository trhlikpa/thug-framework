import datetime
import io
import json
import os
from bson import ObjectId
from celery import Celery
from pymongo import MongoClient
from crawler.useragents import get_useragent_string

# Load config.json file
__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)


@celery.task(bind='true', time_limit=float(config['CRAWLER_TIMELIMIT']))
def execute_job(self, input_data):
    """
    Celery method that uses specified spider to recursively crawl urls
    :param self: Task object self reference
    :param input_data: Dictionary with data for spider
    """

    # Lazy load of task dependencies
    from scrapy.crawler import CrawlerProcess
    from crawler.urlspider import UrlSpider
    from scrapy.http.request import Request

    db_client = MongoClient(config['MONGODB_URL'])
    db = db_client[config['MONGODB_DATABASE']]

    job_id = ObjectId(self.request.id)
    input_data['_state'] = 'STARTED'
    input_data['start_time'] = datetime.datetime.utcnow().isoformat()

    if input_data.get('schedule_id') is not None:
        schedule_id = ObjectId(input_data['schedule_id'])
        query = db.schedules.find_one({'_id': schedule_id}, {'name': 1, 'previous_runs': 1})
        count = len(query['previous_runs']) + 1
        db.schedules.update_one({'_id': schedule_id}, {'$push': {'previous_runs': ObjectId(self.request.id)}})
        input_data['name'] = query['name'] + '_' + str(count)

    db.jobs.update_one({'_id': job_id}, {'$set': input_data}, upsert=True)

    def _crawler_callback(link):
        """
        Callback function that spider executes for every link
        :param link: input link
        """
        from worker.tasks import analyze_url

        data = link.meta
        data['url'] = link.url

        json_data = {
            'url': link.url,
            '_state': 'PENDING',
            'start_time': None,
            'end_time': None,
            'job_id': str(job_id)
        }

        task_id = db.tasks.insert(json_data)
        db.jobs.update_one({'_id': job_id}, {'$push': {'tasks': task_id}})
        analyze_url.apply_async(args=[data], task_id=str(task_id))

    try:
        if input_data.get('type', '') == 'singleurl':
            request = Request(url=input_data['url'], meta=input_data)
            _crawler_callback(request)
        else:
            process = CrawlerProcess({
                'USER_AGENT': get_useragent_string(input_data.get('useragent', None)),
                'DOWNLOAD_DELAY': config['CRAWLER_DOWNLOAD_DELAY']
            })
            process.crawl(UrlSpider, data=input_data, callback=_crawler_callback)
            process.start(True)

        db.jobs.update_one({'_id': job_id}, {'$set': {
            '_state': 'SUCCESS', 'end_time': datetime.datetime.utcnow().isoformat()}})
    except Exception as error:
        db.jobs.update_one({'_id': job_id}, {'$set': {
            '_state': 'FAILURE', 'error': error.message, 'end_time': datetime.datetime.utcnow().isoformat()}})
    finally:
        db_client.close()
