from datetime import datetime, timedelta
from celery.beat import Scheduler, ScheduleEntry
from celery.utils.log import get_logger
from scheduler.celeryapp import celery
from scheduler.dbcontext import db
from celery import current_app

celery.set_current()
logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)


class MongoEntry(ScheduleEntry):
    def __init__(self, schedule, app=None):
        self.app = app or current_app
        super(MongoEntry, self).__init__(app)

    def save(self):
        pass


class MongoScheduler(Scheduler):
    Entry = MongoEntry

    _schedule = None
    _last_updated = None
    _fetch_interval = timedelta(seconds=20)

    def __init__(self, *args, **kwargs):
        super(MongoScheduler, self).__init__(*args, **kwargs)

    def requires_update(self):
        if not self._last_updated:
            return True

        return self._last_updated + self._fetch_interval < datetime.datetime.now()

    def fetch_schedule_from_database(self):
        self.sync()

        schedules = {}

        for schedule in db.schedules.find():
            schedules[schedule['_id']] = self.Entry(schedule=schedule, app=self.app)

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
