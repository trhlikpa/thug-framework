from datetime import datetime, timedelta

from bson import ObjectId
from celery import current_app
from celery.beat import Scheduler, ScheduleEntry
from celery.utils.log import get_logger
from dateutil import parser
from scheduler.celeryapp import celery
from scheduler.dbcontext import db
from scheduler.utils.celeryutils import create_cron_schedule, create_interval_schedule
from scheduler.utils.exceptions import ScheduleFormatError

celery.set_current()

logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)


class MongoEntry(ScheduleEntry):
    def __init__(self, model, app=None):
        self.app = app or current_app

        if not all(x in model for x in ['_id', 'name', 'task', 'enabled', 'args', 'kwargs', 'max_run_count',
                                        'total_run_count', 'last_run_at', 'run_after', 'options']):
            raise ScheduleFormatError('Schedule fields error')

        if 'cron' not in model and 'interval' not in model:
            raise ScheduleFormatError('Cron or interval scheduling is missing')

        self.id = model['_id']
        self.name = model['name']
        self.task = model['task']
        self.enabled = model['enabled']
        self.args = model.get('args') or list()
        self.kwargs = model.get('kwargs') or dict()
        self.options = model.get('options') or dict()

        if model['cron']:
            self.schedule = create_cron_schedule(model['cron'])
        else:
            self.schedule = create_interval_schedule(model['interval'])

        if model['max_run_count'] < 1:
            self.max_run_count = 100
        else:
            self.max_run_count = model['max_run_count']

        if model['total_run_count'] < 1:
            self.total_run_count = 0
        else:
            self.total_run_count = model['total_run_count']

        if not model['last_run_at']:
            self.last_run_at = self.app.now()
        else:
            self.last_run_at = model['last_run_at']

        if not model['run_after']:
            self.run_after = None
        else:
            self.run_after = parser.parse(model['run_after'])

        self.model = model

    def __next__(self):
        now = self.app.now()
        total_run_count = self.total_run_count + 1

        self.last_run_at = now
        self.model['last_run_at'] = now
        self.total_run_count = total_run_count
        self.model['total_run_count'] = total_run_count
        return self.__class__(self.model)

    next = __next__  # for 2to3

    def is_due(self):
        debug('schedule: ' + str(self.id))
        if not self.enabled:
            return False, 5.0   # 5 second delay for re-enable.

        if self.total_run_count >= self.max_run_count:
            return False, 5.0

        if self.run_after and parser.parse(self.run_after) < self.app.now():
            return False, 5.0

        return self.schedule.is_due(self.last_run_at)

    def save(self):
        updated_data = {
            'last_run_at': self.last_run_at,
            'total_run_count': self.total_run_count
        }

        db.schedules.update_one({'_id': ObjectId(self.id)}, {'$set': updated_data})


class MongoScheduler(Scheduler):
    Entry = MongoEntry

    _fetch_interval = timedelta(seconds=20)

    def __init__(self, *args, **kwargs):
        self._schedule = {}
        self._last_updated = None
        Scheduler.__init__(self, *args, **kwargs)

    def requires_update(self):
        if not self._last_updated:
            return True

        return self._last_updated + self._fetch_interval < datetime.now()

    def setup_schedule(self):
        pass

    def fetch_schedule_from_database(self):
        self.sync()

        schedules = {}

        for schedule in db.schedules.find():
            schedules[schedule['_id']] = self.Entry(model=schedule, app=self.app)

        return schedules

    @property
    def schedule(self):
        if self.requires_update():
            self._schedule = self.fetch_schedule_from_database()
            self._last_updated = datetime.now()

        return self._schedule

    def sync(self):
        for entry in self._schedule.values():
            entry.save()
