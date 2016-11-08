import json
from bson import ObjectId
from crawler.tasks import execute_job
from webclient import config
from webclient.api.models.schedules import get_schedule
from webclient.api.utils.celeryutil import normalize_state
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.dbcontext import db


def classify_job(job):
    from webclient.api.models.tasks import get_task
    collums = {'_id': 1,
               '_state': 1,
               'error': 1,
               'exploits': 1
               }

    tasks = list()
    for task_id in job['tasks']:
        if type(task_id) is ObjectId:
            task_id = str(task_id)
        else:
            task_id = task_id['$oid']
        task = get_task(task_id, collums)
        if task['_state'] != 'SUCCESS' and task['_state'] != 'FAILURE':
            return

        tasks.append(task)

    classification = 'CLEAR'

    for task in tasks:
        if task['_state'] == 'FAILURE':
            if classification != 'INFECTED':
                classification = 'SUSPICIOUS'
        elif 'exploits' in task and len(task.get('exploits')) > 0:
            classification = 'INFECTED'

    if type(job['_id']) is not ObjectId:
        tmp = job['_id']['$oid']
    else:
        tmp = str(job['_id'])

    db.jobs.update_one({'_id': ObjectId(tmp)}, {'$set': {'classification': classification}})
    job['classification'] = classification


def get_jobs(args, shedule_id=None):
    """
    Method queries every job from database
    :param shedule_id:
    :param args:
    :return: list of jobs
    """
    normalize_state(db.tasks, float(config['THUG_TIMELIMIT']))
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    filter_fields = None

    if shedule_id is not None:
        schedule = get_schedule(shedule_id)
        jobs_id = schedule['previous_runs']
        filter_fields = {'_id': {'$in': jobs_id}}

    if filter_arg is not None:
        tmp = [{'url': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'name': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}}]
        if filter_fields is not None:
            filter_fields['$or'] = tmp
        else:
            filter_fields = {
                '$or': tmp
            }

    d = get_paged_documents(db.jobs,
                            page=page,
                            pagesize=pagesize,
                            sort=sort,
                            collums=None,
                            filter_fields=filter_fields)

    for entry in d['data']:
        if entry['_state'] == 'SUCCESS' and not entry.get('classification'):
            classify_job(entry)

    json_string = json.dumps(d)
    return json_string


def get_job(job_id):
    """
    Method queries single job from database
    :param job_id: Job id
    :return: job with job_id or None
    """
    normalize_state(db.jobs, float(config['CRAWLER_TIMELIMIT']))
    job = db.jobs.find_one({'_id': ObjectId(job_id)})

    if job is None:
        return None

    if job['_state'] == 'SUCCESS' and not job.get('classification'):
        classify_job(job)

    return job


def create_job(data):
    """
    Method starts url crawling and updates database
    :param data:input data
    :return: job id
    """
    input_data = {x: data[x] if x in data else '' for x in
                  {'useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy', 'depth',
                   'only_internal', 'type', 'name'
                   }}

    json_data = {
        '_state': 'PENDING',
        'classification': None,
        'start_time': None,
        'end_time': None,
        'schedule_id': None,
        'tasks': []
    }

    json_data.update(input_data)

    oid = db.jobs.insert(json_data)

    execute_job.apply_async(args=[input_data], task_id=str(oid))

    return str(oid)


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
