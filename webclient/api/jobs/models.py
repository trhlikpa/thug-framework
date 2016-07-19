from uuid import uuid4
from webclient.dbcontext import db


def get_jobs():
    query = db.jobs.find({}, {'base_url': 1, '_id': 1, 'depth': 1})

    if query.count() != 0:
        return query

    return list()


def get_job(job_id):
    query = db.jobs.find({'_id': job_id})

    if query.count() != 0:
        return query

    return None


def create_job(data):
    uuid = uuid4()

    if not data or 'url' not in data:
        return None

    if 'depth' not in data or data['depth'] < 0:
        return None

    if 'only_internal' not in data:
        return None

    json_data = {
        '_id': str(uuid),
        'base_url': data['url']
    }


def delete_job(job_id):
    pass


def update_job(job_id, **params):
    pass


def pause_job(job_id):
    pass