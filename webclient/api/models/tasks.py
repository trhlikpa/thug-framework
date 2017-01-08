import json
from bson import ObjectId
from webclient.dbcontext import db
from webclient.api.models.jobs import get_job
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from worker.thug.tasks import analyze


def get_tasks(args, job_id=None):
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    filter_fields = None

    if job_id is not None:
        job = get_job(job_id)
        tasks_id = job['tasks']
        filter_fields = {'_id': {'$in': tasks_id}}

    if filter_arg is not None:
        tmp = [{'url': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}}]
        if filter_fields is not None:
            filter_fields['$or'] = tmp
        else:
            filter_fields = {
                '$or': tmp
            }

    collums = {'_id': 1,
               '_state': 1,
               'thug': 1,
               'url': 1,
               'error': 1,
               'start_time': 1,
               'end_time': 1,
               'exploits': 1
               }

    d = get_paged_documents(db.tasks,
                            page=page,
                            pagesize=pagesize,
                            sort=sort,
                            collums=collums,
                            filter_fields=filter_fields)

    json_string = json.dumps(d)
    return json_string


def get_task(task_id, collums=None):
    task = db.tasks.find_one({'_id': ObjectId(task_id)}, collums is None if {} else collums)

    return task


def create_task(data):
    json_data = {
        '_state': 'PENDING',
        'start_time': None,
        'end_time': None
    }

    oid = db.tasks.insert(json_data)

    input_data = {x: data[x] if x in data else ''
                  for x in ['useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy']}

    analyze.apply_async(args=[input_data], task_id=str(oid))
    return str(oid)


def delete_task(task_id):
    analyze.AsyncResult(task_id).revoke()
    result_db = db.tasks.delete_one({'_id': ObjectId(task_id)})

    if result_db.deleted_count > 0:
        return True

    return False
