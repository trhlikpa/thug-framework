from uuid import uuid4
from webclient.dbcontext import db
from webclient.api.tasks.models import create_task
from crawler.tasks import crawl_urls


def get_jobs():
    query = db.jobs.find({}, {'_id': 1, '_state': 1, 'base_url': 1, 'depth': 1, 'tasks': 1})

    if query.count() != 0:
        return query

    return list()


def get_job(job_id):
    query = db.jobs.find({'_id': job_id})

    if query.count() != 0:
        return query

    return None


def create_job(data):
    uuid = str(uuid4())

    if not data or 'url' not in data:
        return None

    if 'depth' not in data or data['depth'] < 0:
        return None

    if 'only_internal' not in data:
        return None

    json_data = {
        '_id': uuid,
        '_state': 'PENDING',
        'base_url': data['url'],
        'depth': data['depth'],
        'tasks': []
    }

    db.jobs.insert(json_data)

    input_data = {x: data[x] if x in data else ''
                  for x in ['useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy', 'depth', 'only_internal']}

    job = crawl_urls.apply_async(args=[input_data], task_id=uuid)
    return job.id


def delete_job(job_id):
    pass


def update_job(job_id, **params):
    pass


def pause_job(job_id):
    pass
