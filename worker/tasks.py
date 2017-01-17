from datetime import datetime
from bson import ObjectId
from worker.dbcontext import db
from worker.celeryapp import celery
from worker.crawler.tasks import crawl
from worker.thug.tasks import analyze
from celery.signals import after_task_publish
from ast import literal_eval as make_tuple

celery.autodiscover_tasks(['worker.crawler, worker.thug'])


def execute_job(url, user_agent, submitter_id, job_name, job_type, job_args,
                crawler_time_limit=None, thug_time_limit=None):
    submit_time = str(datetime.utcnow().isoformat())

    if url is None:
        raise AttributeError('URL is missing')

    if user_agent is None:
        user_agent = 'winxpie60'

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

    job_id = ObjectId()

    json_data = {
        '_id': job_id,
        '_state': 'PENDING',
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
        'tasks': []
    }

    db.jobs.insert_one(json_data)

    signatures = []

    thug_signature = analyze.signature(time_limit=thug_time_limit)
    signatures.append(thug_signature)

    if job_type == 'singleurl':
        for sig in signatures:
            task_id = ObjectId()
            sig.apply_async(args=[str(job_id), url], task_id=str(task_id))
    else:
        crawl.apply_async(args=[signatures], task_id=str(job_id), time_limit=crawler_time_limit)

    return str(job_id)


def revoke_job(job_id):
    pass


@after_task_publish.connect(sender='worker.thug.tasks.analyze')
def thug_sent_handler(sender=None, headers=None, body=None, **kwargs):
    submit_time = str(datetime.utcnow().isoformat())

    info = headers if 'task' in headers else body
    job_id = ObjectId(make_tuple(info['argsrepr'])[0])

    after_publish_data = {
        '_id': ObjectId(info['id']),
        '_state': 'PENDING',
        '_error': None,
        'submit_time': submit_time,
        'start_time': None,
        'end_time': None,
        'job_id': job_id,
        'classification': None
    }

    db.thugtasks.insert_one(after_publish_data)


@after_task_publish.connect(sender='worker.geolocation.tasks.locate')
def geolocation_sent_handler(sender=None, headers=None, body=None, **kwargs):
    pass
