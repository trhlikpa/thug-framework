from datetime import datetime
from bson import ObjectId
from worker.celeryapp import celery
from worker.dbcontext import db


@celery.task(bind=True)
def analyze(self, job_id, url, submitter_id):
    """
    Analyses url with use of thug honeypot and saves results in mongo database

    :param self: celery task object
    :param job_id: job ID to load configuration with
    :param url: url to analyze
    :param submitter_id: submitter email
    """
    # Lazy load of task dependencies
    from thugapi import Thug
    from worker.utils.netutils import check_url
    from worker.utils.useragents import get_useragent_string
    from worker.utils.exceptions import DatabaseRecordError, UserAgentNotFoundError
    from worker.utils.exceptions import UrlNotFoundError, UrlNotReachedError
    from worker.utils.geolocation import geolocate

    output_data = dict()

    try:
        job = db.jobs.find_one({'_id': ObjectId(job_id)})

        if job is None:
            raise DatabaseRecordError('Job not found in database')

        if url is None:
            raise UrlNotFoundError('URL is missing')

        if submitter_id is None:
            raise DatabaseRecordError('Submitter not found')

        if not check_url(url):
            raise UrlNotReachedError('Specified URL cannot be reached')

        args = job.get('args')

        if args is None:
            raise DatabaseRecordError('Job record has incorrect format')

        user_agent = job.get('useragent')

        if get_useragent_string(user_agent) is None:
            raise UserAgentNotFoundError('User agent not found')

        job_type = job.get('type')

        start_time = datetime.utcnow().isoformat()

        initial_output_data = {
            '_state': 'STARTED',
            'start_time': start_time,
        }

        job_output_data = {
            '_current_url': url
        }

        if job_type == 'singleurl':
            job_output_data.update(initial_output_data)

        db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': job_output_data})
        db.tasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': initial_output_data})

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
            no_cache=bool(args.get('no_cache')),
            web_tracking=bool(args.get('web_tracking')),
            url_classifiers=args.get('url_classifiers'),
            html_classifiers=args.get('html_classifiers'),
            js_classifiers=args.get('js_classifiers'),
            vb_classifiers=args.get('vb_classifiers'),
            sample_classifiers=args.get('sample_classifiers')
        )

        # classifying task
        exploits = db.exploits.find_one({'analysis_id': ObjectId(analysis_id)})

        classification = 'CLEAR'

        if exploits is not None:
            classification = 'MALICIOUS'

        output_data = {
            '_state': 'SUCCESSFUL',
            'analysis_id': ObjectId(analysis_id),
            'classification': classification
        }

        # task geolocation
        geolocation_id = geolocate(url)
        output_data['geolocation_id'] = ObjectId(geolocation_id)

    except (DatabaseRecordError, UserAgentNotFoundError, UrlNotFoundError, UrlNotReachedError, IOError) as error:
        output_data = {
            '_state': 'FAILURE',
            '_error': str(error),
            'classification': 'SUSPICIOUS'
        }

    finally:
        end_time = datetime.utcnow().isoformat()

        output_data['end_time'] = end_time

        db.tasks.update_one({'_id': ObjectId(self.request.id)}, {'$set': output_data})
