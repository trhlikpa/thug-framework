import io
import json
import os
import datetime
from worker.celeryapp import celery
from worker.dbcontext import db


@celery.task(bind=True)
def analyze(self, job_id):
    try:
        # Lazy load of task dependencies
        from thugapi import Thug
        from worker.utils.geolocation import query_info
        from worker.utils.netutils import hostname_to_ip
        from worker.utils.exceptions import DatabaseRecordError

        job = db.jobs.find_one({'_id': job_id})

        if job is None:
            raise DatabaseRecordError('Job not found in database')

        url = job.get('url')

        if url is None:
            raise AttributeError('URL is missing')

        args = job.get('args')

        if args is None:
            raise DatabaseRecordError('Job record has incorrect format')

        user_agent = job.get('useragent')

        if user_agent is None:
            raise ValueError('User agent not found')

        job_type = job.get('type')

        start_time = str(datetime.datetime.utcnow().isoformat())

        initial_output_data = {
            '_state': 'STARTED',
            'start_time': start_time,
        }

        if job_type == 'singleurl':
            db.jobs.update_one({'_id': job_id}, {'$set': initial_output_data})

        db.tasks.update_one({'_id': self.request.id}, {'$set': initial_output_data})

    except Exception as error:
        pass
