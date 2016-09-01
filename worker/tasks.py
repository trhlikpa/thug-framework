import io
import json
import os
import socket
import datetime
import pytz
from urlparse import urlparse
from celery import Celery
from pymongo import MongoClient


# Load config file
__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

# Start celery and connect to redis
celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)

TIMEZONE = pytz.timezone(config['CELERY_TIMEZONE'])


def get_ip(url):
    """
    Method resloves hostname to ip address
    :param url: url to resolve
    :return: ip address
    """
    netloc = urlparse(url).netloc
    dom = netloc.split('@')[-1].split(':')[0]
    return socket.gethostbyname(dom)


@celery.task(bind='true', time_limit=float(config['THUG_TIMELIMIT']))
def analyze_url(self, input_data):
    """
    Method puts new task into thug workers queue
    :param self: self reference
    :param input_data: input data
    """

    # lazy load of task dependencies
    from thugapi import Thug
    from geoloc import get_geoloc_info

    db_client = MongoClient(config['MONGODB_URL'])
    db = db_client[config['MONGODB_DATABASE']]

    uuid = str(self.request.id)

    db.tasks.update_one({'_id': uuid}, {'$set': {
        '_state': 'STARTED', 'start_time': datetime.datetime.now(TIMEZONE)}}, upsert=True)

    output_data = dict()
    output_data['_state'] = 'FAILURE'

    try:
        ip = get_ip(input_data['url'])
        geoloc_data = get_geoloc_info(ip)
        output_data['geolocation'] = geoloc_data.__dict__
    except Exception as error:
        geoloc_data = dict(error=error.message)
        output_data['geolocation'] = geoloc_data

    try:
        thug = Thug(input_data)
        log_path = thug.analyze()
        json_path = os.path.join(log_path, 'analysis/json/analysis.json')

        with io.open(json_path) as result:
            thug_data = json.load(result)
            output_data['_state'] = 'SUCCESS'
            output_data.update(thug_data)
    except Exception as error:
        output_data['_state'] = 'FAILURE'
        output_data['error'] = error.message
    finally:
        output_data['end_time'] = datetime.datetime.now(TIMEZONE)
        db.tasks.update_one({'_id': uuid}, {'$set': output_data}, upsert=True)
        db_client.close()
