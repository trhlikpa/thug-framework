import json
from webclient.dbcontext import db
from webclient.api.models.schedules import get_schedule
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from worker.tasks import execute_job, revoke_job

'''
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

'''


def get_jobs(args, shedule_id=None):
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
    '''
    for entry in d['data']:
        if entry['_state'] == 'SUCCESS' and not entry.get('classification'):
            classify_job(entry)
    '''

    json_string = json.dumps(d)
    return json_string


def get_job(job_id):
    job = db.jobs.find_one({'_id': job_id})

    if job is None:
        return None

    '''
    if job['_state'] == 'SUCCESS' and not job.get('classification'):
        classify_job(job)
    '''

    return job


def create_job(data):
    job_type = data.get('type')
    job_name = data.get('name')
    submitter_id = data.get('submitter_id')

    job_args = {x: data[x] if x in data else None for x in
                  {'useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy', 'depth_limit', 'only_internal',
                   'download_delay', 'randomize_download_delay', 'redirect_max_times', 'robotstxt_obey'
                   }}

    job_id = execute_job(submitter_id=submitter_id, job_type=job_type, job_name=job_name, job_args=job_args)

    return job_id


def delete_job(job_id):
    revoke_job(job_id)

    return job_id
