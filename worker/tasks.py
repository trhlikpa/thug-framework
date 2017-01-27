from datetime import datetime
from bson import ObjectId
from worker.dbcontext import db
from worker.celeryapp import celery
from worker.crawler.tasks import crawl
from worker.analyzer.tasks import analyze
from celery.signals import after_task_publish
from ast import literal_eval as make_tuple

celery.autodiscover_tasks(['worker.crawler, worker.analyzer'])


@celery.task()
def execute_job(data):
    submit_time = str(datetime.utcnow().isoformat())

    job_id = ObjectId()

    data['_id'] = job_id
    data['submit_time'] = submit_time

    db.jobs.insert_one(data)

    signatures = []

    thug_signature = analyze.signature(time_limit=data['thug_time_limit'])
    signatures.append(thug_signature)

    if data['type'] == 'singleurl':
        for sig in signatures:
            task_id = ObjectId()
            sig.apply_async(args=[str(job_id), data['url']], task_id=str(task_id))
    else:
        crawl.apply_async(args=[signatures], task_id=str(job_id), time_limit=data['crawler_time_limit'])

    return str(job_id)


@after_task_publish.connect(sender='worker.analyzer.tasks.analyze')
def thug_sent_handler(headers=None, body=None, **kwargs):
    submit_time = str(datetime.utcnow().isoformat())

    info = headers if 'task' in headers else body
    job_id = ObjectId(make_tuple(info['argsrepr'])[0])
    url = make_tuple(info['argsrepr'])[1]

    after_publish_data = {
        '_id': ObjectId(info['id']),
        '_state': 'PENDING',
        '_error': None,
        'url': url,
        'submit_time': submit_time,
        'start_time': None,
        'end_time': None,
        'job_id': job_id,
        'analysis_id': None,
        'geolocation_id': None,
        'classification': None
    }

    db.tasks.insert_one(after_publish_data)
    db.jobs.update_one({'_id': job_id}, {'$push': {'tasks': ObjectId(info['id'])}})


def revoke_job(job_id):
    pass


def revoke_task(task_id):
    pass
