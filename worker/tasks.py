import io
import json
import os
from celery import Celery
from httplib2 import Http, HttpLib2Error
from pymongo import MongoClient
from thugapi import Thug

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)

db_client = MongoClient(config['MONGODB_URL'])
db = db_client.thug_database


def is_url_alive(url):
    http = Http()
    response = http.request(url, 'HEAD')
    if int(response[0]['status']) < 400:
        return True

    return False


@celery.task(bind='true', time_limit=1800)
def analyze_url(self, data):
    uuid = self.request.id

    json_data = dict(_state='STARTED')

    db.tasks.update({'_id': str(uuid)}, json_data)

    try:
        thug = Thug(data)

        if not is_url_alive(data['url']):
            raise ValueError('URL cannot be reached')

        log_path = thug.analyze()
        json_path = os.path.join(log_path, 'analysis/json/analysis.json')

        with io.open(json_path) as result:
            data = json.load(result)
            json_data['_state'] = 'SUCCESS'
            json_data.update(data)
    except (HttpLib2Error, ValueError) as error:
        json_data['_state'] = 'FAILURE'
        json_data['error'] = error.message
    finally:
        db.tasks.update({'_id': str(uuid)}, json_data)
        db_client.close()


@celery.task(bind='true', time_limit=120)
def crawl_urls(base_url):
    pass
