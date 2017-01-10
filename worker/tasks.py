from worker.dbcontext import db
from worker.celeryapp import celery
from worker.crawler.tasks import crawl
from uuid import uuid4

celery.autodiscover_tasks(['worker.crawler, worker.thug'])


def execute_job(submitter_id, job_name, job_type, job_args):

    job_id = str(uuid4())

    json_data = {
        '_id': job_id,
        '_state': 'PENDING',
        '_substate': None,
        '_current_url': None,
        '_error': None,
        'type': job_type,
        'name': job_name,
        'useragent': None,
        'classification': None,
        'submit_time': None,
        'start_time': None,
        'end_time': None,
        'crawler_start_time': None,
        'crawler_end_time': None,
        'submitter_id': submitter_id,
        'schedule_id': None,
        'args': job_args,
        'urls': []
    }

    db.jobs.insert_one(json_data)

    crawl.apply_async(task_id=job_id)

    return job_id


def revoke_job(job_id):
    pass
