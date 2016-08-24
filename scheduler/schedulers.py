import datetime
import json
import os
import io
from celery import Celery
from celerybeatmongo.schedulers import MongoScheduler

# Load config file
__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

# Start celery and connect to redis
celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)
celery.conf.update({
    "CELERY_MONGODB_SCHEDULER_COLLECTION": "schedules",
    "CELERY_MONGODB_SCHEDULER_DB": config['MONGODB_DATABASE'],
    "CELERY_MONGODB_SCHEDULER_URL": config['MONGODB_URL']
})


class CustomMongoScheduler(MongoScheduler):
    def __init__(self, *args, **kwargs):
        super(CustomMongoScheduler, self).__init__(*args, **kwargs)
        self.UPDATE_INTERVAL = datetime.timedelta(seconds=15)
