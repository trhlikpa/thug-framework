from celery import Celery
from time import sleep
import json

with open('../config.json') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)


@celery.task
def add(x):
    sleep(30)
    return x
