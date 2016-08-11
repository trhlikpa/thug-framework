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


@celery.task(bind='true', time_limit=600)
def analyze_url(self, data):

    from thugapi import Thug

    db_client = MongoClient(config['MONGODB_URL'])
    db = db_client.thug_database

    uuid = str(self.request.id)
    json_data = {
        '_state': 'STARTED',
        'url': data['url']
    }

    db.tasks.update({'_id': uuid}, json_data, True)

    json_data['_state'] = 'FAILURE'

    try:
        thug = Thug(data)
        log_path = thug.analyze()
        json_path = os.path.join(log_path, 'analysis/json/analysis.json')

        with io.open(json_path) as result:
            data = json.load(result)
            json_data['_state'] = 'SUCCESS'
            json_data.update(data)
    except Exception as error:
        json_data['_state'] = 'FAILURE'
        json_data['error'] = error.message
    finally:
        db.tasks.update({'_id': uuid}, json_data)
        db_client.close()
