import datetime
import json
import os
import io
import traceback
import sys
from bson import ObjectId
from celery import Celery
from celery.beat import SchedulingError
from celerybeatmongo.schedulers import MongoScheduler
from celery.utils.log import get_logger
from celery.five import reraise

logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)

# Load config file
__dir__ = os.path.dirname(os.path.realpath(__file__))
with io.open(os.path.join(__dir__, '../config.json'), encoding='utf8') as f:
    config = json.load(f)

# Start celery and connect to redis
celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)
celery.conf.update({
    'CELERY_MONGODB_SCHEDULER_COLLECTION': 'schedules',
    'CELERY_MONGODB_SCHEDULER_DB': config['MONGODB_DATABASE'],
    'CELERY_MONGODB_SCHEDULER_URL': config['MONGODB_URL']
})


class CustomMongoScheduler(MongoScheduler):
    def send_task(self, *args, **kwargs):
        return self.app.send_task(task_id=str(ObjectId()), *args, **kwargs)

    def apply_async(self, entry, publisher=None, **kwargs):
        # Update timestamps and run counts before we actually execute,
        # so we have that done if an exception is raised (doesn't schedule
        # forever.)
        entry = self.reserve(entry)
        task = self.app.tasks.get(entry.task)

        try:
            if task:
                result = task.apply_async(entry.args, entry.kwargs,
                                          publisher=publisher, task_id=str(ObjectId()),
                                          **entry.options)
            else:
                result = self.send_task(entry.task, entry.args, entry.kwargs,
                                        publisher=publisher, **entry.options)
        except Exception as exc:
            reraise(SchedulingError, SchedulingError(
                "Couldn't apply scheduled task {0.name}: {exc}".format(
                    entry, exc=exc)), sys.exc_info()[2])
        finally:
            self._tasks_since_sync += 1
            if self.should_sync():
                self._do_sync()
        return result

    def __init__(self, *args, **kwargs):
        super(CustomMongoScheduler, self).__init__(*args, **kwargs)
        self.UPDATE_INTERVAL = datetime.timedelta(seconds=15)
