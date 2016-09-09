from bson import ObjectId
from crawler.tasks import execute_job
from webclient.dbcontext import db


def get_jobs():
    """
    Method queries every job from database
    :return: list of jobs
    """
    query = db.jobs.find()

    if query.count() != 0:
        return query

    return list()


def get_job(job_id):
    """
    Method queries single job from database
    :param job_id: Job id
    :return: job with job_id or None
    """
    job = db.jobs.find_one({'_id': ObjectId(job_id)})

    if job is None:
        return None

    return job


def create_job(data):
    """
    Method starts url crawling and updates database
    :param data:input data
    :return: job id
    """
    input_data = {x: data[x] if x in data else '' for x in
                  {'useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy', 'depth',
                   'only_internal', 'type'
                   }}

    json_data = {
        '_state': 'PENDING',
        'tasks': []
    }

    json_data.update(input_data)

    oid = db.jobs.insert(json_data)

    execute_job.apply_async(args=[input_data], task_id=str(oid))

    return oid


def delete_job(job_id):
    """
    Method deletes job
    TODO
    :param job_id: job id
    """
    execute_job.AsyncResult(job_id).revoke()
    result_db = db.jobs.delete_one({'_id': ObjectId(job_id)})

    if result_db.deleted_count > 0:
        return True

    return False


def update_job(job_id, **params):
    """
    Method updates job
    TODO
    :param job_id: job id
    :param params: new parameters
    """
    pass


def pause_job(job_id):
    """
    Method pauses job
    TODO
    :param job_id: job id
    """
    pass
