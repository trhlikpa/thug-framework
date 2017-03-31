# Copyright 2013 Regents of the University of Michigan

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# https://github.com/zmap/celerybeat-mongo
#
# Modifications  2017 Pavel Trhlik
#
import sys
from datetime import datetime, timedelta
from billiard.five import reraise
from bson import ObjectId
from celery import current_app
from celery.beat import Scheduler, ScheduleEntry, SchedulingError
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


# Celery beat wake up interval
MAX_INTERVAL = 2 * 60


class MongoEntry(ScheduleEntry):
    """ A mongodb entry in the scheduler """

    def __init__(self, model, app=None):
        """
        :param model: schedule mongodb document
        :param app: celery app
        """
        self.app = app or current_app
        self.model = model
        self.id = str(model['_id'])

        if not all(x in model for x in ['name', 'task', 'enabled', 'args', 'kwargs', 'max_run_count',
                                        'total_run_count', 'last_run_at', 'run_after', 'options']):
            raise ScheduleFormatError('Schedule fields error')

        if 'cron' not in model and 'interval' not in model:
            info('Cron or interval scheduling missing: disabling schedule id: ' + self.id)
            self.enabled = False
            self.model['enabled'] = False
        else:
            if model['cron']:
                self.schedule = create_cron_schedule(model['cron'])
            else:
                self.schedule = create_interval_schedule(model['interval'])

        self.name = model['name']
        self.task = model['task']
        self.enabled = model['enabled']
        self.args = model.get('args') or list()
        self.kwargs = model.get('kwargs') or dict()
        self.options = model.get('options') or dict()

        if self.model['max_run_count'] < 1:
            self.model['max_run_count'] = 100

        self.max_run_count = self.model['max_run_count']

        if self.model['total_run_count'] < 1:
            self.model['total_run_count'] = 0

        self.total_run_count = self.model['total_run_count']

        if not self.model['last_run_at']:
            self.model['last_run_at'] = self.app.now()

        self.last_run_at = self.model['last_run_at']

        if self.model['run_after']:
            self.model['run_after'] = parser.parse(self.model['run_after'])

        self.run_after = self.model['run_after']

        # Fix name of the next job iteration
        self.model['args'][0]['name'] = self.name + '_' + str(self.total_run_count)
        self.args[0]['name'] = self.model['args'][0]['name']

    def __next__(self):
        """
        Returns new MongoEntry instance with updated fields
        """
        self.model['last_run_at'] = self.app.now()
        self.model['total_run_count'] += 1
        return self.__class__(self.model)

    next = __next__  # for 2to3

    def is_due(self):
        """
        Checks if task should be executed
        """
        if not self.model['enabled']:
            return False, MAX_INTERVAL

        if self.model['total_run_count'] >= self.model['max_run_count']:
            return False, MAX_INTERVAL

        if self.model['run_after'] and self.model['run_after'] < self.app.now():
            return False, MAX_INTERVAL

        return self.schedule.is_due(self.last_run_at)

    def save(self):
        """
        Saves relevant MongoEntry fields to the database
        """
        updated_data = {
            'last_run_at': self.model['last_run_at'],
            'total_run_count': self.model['total_run_count'],
        }

        if self.model['enabled'] and self.model['total_run_count'] < self.model['max_run_count']:
            updated_data['next_run'] = (datetime.utcnow() + self.schedule.remaining_estimate(
                self.model['last_run_at'])).isoformat()
        else:
            updated_data['next_run'] = None

        db.schedules.update_one({'_id': ObjectId(self.id)}, {'$set': updated_data})


class MongoScheduler(Scheduler):
    """ Scheduler with mongodb backend """
    Entry = MongoEntry

    _fetch_interval = timedelta(seconds=10)

    max_interval = MAX_INTERVAL

    def __init__(self, *args, **kwargs):
        self._schedule = {}
        self._last_updated = None
        Scheduler.__init__(self, *args, **kwargs)

    def send_task(self, *args, **kwargs):
        return self.app.send_task(task_id=str(ObjectId()), *args, **kwargs)

    def apply_async(self, entry, publisher=None, **kwargs):
        entry = self.reserve(entry)
        task = self.app.tasks.get(entry.task)

        try:
            if task:
                result = task.apply_async(entry.args, entry.kwargs,
                                          publisher=publisher, task_id=str(ObjectId()), **entry.options)
            else:
                result = self.send_task(entry.task, entry.args, entry.kwargs,
                                        publisher=publisher, **entry.options)

            db.schedules.update_one({'_id': ObjectId(entry.id)}, {'$push': {'previous_runs': ObjectId(result.task_id)}})
        except Exception as exc:
            reraise(SchedulingError, SchedulingError(
                "Couldn't apply scheduled task {0.name}: {exc}".format(
                    entry, exc=exc)), sys.exc_info()[2])
        finally:
            self._tasks_since_sync += 1
            if self.should_sync():
                self._do_sync()

        return result

    def install_default_entries(self, data):
        pass

    def requires_update(self):
        """
        Ensures there is minimum timedelta between updates
        """
        if not self._last_updated:
            return True

        return self._last_updated + self._fetch_interval < datetime.now()

    def get_from_database(self):
        """
        Updates schedule from database

        :return: updated schedule
        """
        self.sync()
        schedules = {}

        for schedule in db.schedules.find():
            schedules[str(schedule['_id'])] = self.Entry(model=schedule, app=self.app)

        return schedules

    @property
    def schedule(self):
        """
        MongoEntry map
        """
        if self.requires_update():
            self._schedule = self.get_from_database()
            self._last_updated = datetime.now()

        return self._schedule

    def sync(self):
        """
        Saves MongoEntry instances
        """
        for entry in self._schedule.values():
            entry.save()
