from datetime import datetime
from bson import ObjectId
from worker.celeryapp import celery
from worker.dbcontext import db
from worker.utils.exceptions import DatabaseRecordError, UserAgentNotFoundError, UrlNotFoundError
from worker.utils.geolocation import geolocate


@celery.task(bind=True)
def analyze(self, job_id, url):
    try:
        # Lazy load of task dependencies
        from thugapi import Thug
        from worker.utils.useragents import get_useragent_string

        job = db.jobs.find_one({'_id': ObjectId(job_id)})

        if job is None:
            raise DatabaseRecordError('Job not found in database')

        if url is None:
            raise UrlNotFoundError('URL is missing')

        args = job.get('args')

        if args is None:
            raise DatabaseRecordError('Job record has incorrect format')

        user_agent = job.get('useragent')

        if get_useragent_string(user_agent) is None:
            raise UserAgentNotFoundError('User agent not found')

        job_type = job.get('type')

        start_time = str(datetime.utcnow().isoformat())

        initial_output_data = {
            '_state': 'STARTED',
            'start_time': start_time,
        }

        if job_type == 'singleurl':
            db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': initial_output_data})

        db.tasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': initial_output_data}, upsert=True)

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
            url_classifiers=args.get('url_classifiers'),
            html_classifiers=args.get('html_classifiers'),
            js_classifiers=args.get('js_classifiers'),
            vb_classifiers=args.get('vb_classifiers'),
            sample_classifiers=args.get('sample_classifiers')
        )

        end_time = str(datetime.utcnow().isoformat())

        exploits = db.exploits.find_one({'analysis_id': ObjectId(analysis_id)})

        classification = 'CLEAR'

        if exploits is not None:
            classification = 'INFECTED'

        geolocation_id = geolocate(url)

        success_output_data = {
            '_state': 'SUCCESSFUL',
            'end_time': end_time,
            'analysis_id': ObjectId(analysis_id),
            'classification': classification,
            'geolocation_id': ObjectId(geolocation_id)
        }

        db.tasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': success_output_data})

    except (DatabaseRecordError, UserAgentNotFoundError, UrlNotFoundError) as error:
        end_time = str(datetime.utcnow().isoformat())

        failure_output_data = {
            '_state': 'FAILURE',
            '_error': error.message,
            'end_time': end_time,
            'analysis_id': None,
            'classification': 'SUSPICIOUS'
        }

        db.tasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': failure_output_data})
