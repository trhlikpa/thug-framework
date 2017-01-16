from datetime import datetime
from bson import ObjectId
from worker.celeryapp import celery
from worker.dbcontext import db
from worker.utils.exceptions import DatabaseRecordError


@celery.task(bind=True)
def analyze(self, url, job_id):
    try:
        # Lazy load of task dependencies
        from thugapi import Thug
        from worker.utils.useragents import get_useragent_string

        job = db.jobs.find_one({'_id': ObjectId(job_id)})

        if job is None:
            raise DatabaseRecordError('Job not found in database')

        if url is None:
            raise AttributeError('URL is missing')

        args = job.get('args')

        if args is None:
            raise DatabaseRecordError('Job record has incorrect format')

        user_agent = job.get('useragent')

        if get_useragent_string(user_agent) is None:
            raise ValueError('User agent not found')

        job_type = job.get('type')

        start_time = str(datetime.utcnow().isoformat())

        initial_output_data = {
            '_state': 'STARTED',
            'start_time': start_time,
        }

        if job_type == 'singleurl':
            db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': initial_output_data})

        db.thugtasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': initial_output_data}, upsert=True)

        thug = Thug()

        analysis_id = thug.analyze_url(
                         url=url,
                         useragent=user_agent,
                         referer=args.get('referer'),
                         java=args.get('java'),
                         shockwave=args.get('shockwave'),
                         adobepdf=args.get('adobepdf'),
                         proxy=args.get('proxy'),
                         dom_events=args.get('dom_events'),
                         no_cache=args.get('no_cache', False),
                         web_tracking=args.get('web_tracking', False),
                         timeout=args.get('timeout'),
                         url_classifiers=args.get('url_classifiers'),
                         html_classifiers=args.get('html_classifiers'),
                         js_classifiers=args.get('js_classifiers'),
                         vb_classifiers=args.get('vb_classifiers'),
                         sample_classifiers=args.get('sample_classifiers')
                         )

        end_time = str(datetime.utcnow().isoformat())

        success_output_data = {
            '_state': 'SUCCESSFUL',
            'end_time': end_time,
            'analysis_id': ObjectId(analysis_id)
        }

        db.thugtasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': success_output_data})

    except Exception as error:
        end_time = str(datetime.utcnow().isoformat())

        failure_output_data = {
            '_state': 'FAILURE',
            '_error': error.message,
            'end_time': end_time,
            'analysis_id': None
        }

        db.thugtasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': failure_output_data})
