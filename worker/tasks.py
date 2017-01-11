import datetime
from worker.dbcontext import db
from worker.celeryapp import celery
from worker.crawler.tasks import crawl
from uuid import uuid4

celery.autodiscover_tasks(['worker.crawler, worker.thug'])


def execute_job(url, user_agent, submitter_id, job_name, job_type, job_args,
                crawler_time_limit=None, thug_time_limit=None):

    job_id = str(uuid4())

    submit_time = str(datetime.datetime.utcnow().isoformat())

    if url is None:
        raise AttributeError('URL is missing')

    if user_agent is None:
        user_agent = 'winxpie60'

    job_args['java'] = job_args.get('java')
    job_args['shockwave'] = job_args.get('shockwave')
    job_args['adobepdf'] = job_args.get('adobepdf')
    job_args['proxy'] = job_args.get('proxy')
    job_args['allowed_domains'] = job_args.get('allowed_domains')
    job_args['depth_limit'] = job_args.get('depth_limit', 1)
    job_args['only_internal'] = job_args.get('only_internal', True)
    job_args['download_delay'] = job_args.get('download_delay', 0)
    job_args['randomize_download_delay'] = job_args.get('randomize_download_delay', False)
    job_args['redirect_max_times'] = job_args.get('redirect_max_times', 30)
    job_args['robotstxt_obey'] = job_args.get('robotstxt_obey', False)

    if job_args.get('depth_limit') is None:
        job_args['depth_limit'] = 1

    if job_args.get('only_internal') is None:
        job_args['only_internal'] = True

    if job_args.get('download_delay') is None:
        job_args['download_delay'] = 0

    if job_args.get('randomize_download_delay') is None:
        job_args['randomize_download_delay'] = False

    if job_args.get('redirect_max_times') is None:
        job_args['redirect_max_times'] = 30

    if job_args.get('robotstxt_obey') is None:
        job_args['robotstxt_obey'] = False

    json_data = {
        '_id': job_id,
        '_state': 'PENDING',
        '_substate': None,
        '_current_url': None,
        '_error': None,
        'type': job_type,
        'name': job_name,
        'url': url,
        'useragent': user_agent,
        'classification': None,
        'submit_time': submit_time,
        'start_time': None,
        'end_time': None,
        'crawler_start_time': None,
        'crawler_end_time': None,
        'crawler_time_limit': crawler_time_limit,
        'thug_time_limit': thug_time_limit,
        'submitter_id': submitter_id,
        'schedule_id': None,
        'args': job_args,
        'urls': []
    }

    db.jobs.insert_one(json_data)

    crawl.apply_async(task_id=job_id, time_limit=crawler_time_limit)

    return job_id


def revoke_job(job_id):
    pass
