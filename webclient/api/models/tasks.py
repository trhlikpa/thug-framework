import json
from bson import ObjectId
from webclient.dbcontext import db
from webclient.api.models.jobs import get_job
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.api.utils.celeryutils import normalize_task_states
from worker.tasks import revoke_task


def get_tasks(args, job_id=None):
    normalize_task_states()
    page, pagesize, sort, _ = parse_url_parameters(args)

    filter_fields = None

    if job_id is not None:
        job = get_job(job_id)
        tasks_id = job['tasks']
        filter_fields = {'_id': {'$in': tasks_id}}

    d = get_paged_documents(db.tasks,
                            page=page,
                            pagesize=pagesize,
                            sort=sort,
                            filter_fields=filter_fields
                            )

    json_string = json.dumps(d)
    return json_string


def get_task(task_id):
    normalize_task_states()
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    return task


def delete_task(task_id):
    revoke_task(task_id)


def get_task_geolocation(task_id):
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    geolocation = db.geolocation.find_one({'_id': ObjectId(task['geolocation_id'])})

    return geolocation


def get_task_subresource(task_id, resource_name):
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    analysis = db.analyses.find_one({'_id': ObjectId(task['analysis_id'])})

    if resource_name == 'options':
        resource = [analysis]
    else:
        resource = db[resource_name].find({'analysis_id': ObjectId(analysis['_id'])})

    tmp_dict = list()

    for entry in resource:
        new_entry = dict(entry)

        if entry.get('url_id'):
            url = db.urls.find_one({'_id': ObjectId(entry['url_id'])})
            new_entry['url'] = url['url']

        if entry.get('source_id'):
            url = db.urls.find_one({'_id': ObjectId(entry['source_id'])})
            new_entry['source_url'] = url['url']

        if entry.get('destination_id'):
            url = db.urls.find_one({'_id': ObjectId(entry['destination_id'])})
            new_entry['destination_url'] = url['url']

        tmp_dict.append(new_entry)

    return tmp_dict
