import json
from bson import ObjectId
from webclient.dbcontext import db
from webclient.api.models.jobs import get_job
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.api.utils.celeryutils import normalize_task_states
from worker.tasks import revoke_task


def get_tasks(args, job_id=None):
    """
    Returns list of tasks

    :param args: pagination and filtering arguments
    :param job_id: job ID
    """
    normalize_task_states()
    page, pagesize, sort, filter_args = parse_url_parameters(args)

    filter_fields = {}

    if job_id is not None:
        job = get_job(job_id)

        if not job:
            return list()

        tasks_id = job['tasks']
        filter_fields = {'_id': {'$in': tasks_id}}

    if filter_args:
        tmp = []

        for filter_arg in filter_args:
            values = filter_arg['values']
            field = filter_arg['field']
            value = '|'.join(map(str, values))
            regex = {'$regex': '.*(' + value + ').*', '$options': 'ix'}

            if field == 'all':
                tmp.extend([{'url': regex},
                            {'_state': regex},
                            {'end_time': regex},
                            {'classification': regex}])
                break

        if len(tmp) > 0:
            filter_fields['$or'] = tmp

    tasks = get_paged_documents(db.tasks,
                                page=page,
                                pagesize=pagesize,
                                sort=sort,
                                filter_fields=filter_fields
                                )

    json_string = json.dumps(tasks)
    return json_string


def get_task(task_id):
    """
    Returns task with specified task_id

    :param task_id: task ID
    """
    normalize_task_states()
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    return task


def delete_task(task_id):
    """
    Deletes task with specified task_id

    :param task_id: task ID
    :return: True if successful, False otherwise
    """
    return revoke_task(task_id)


def get_task_geolocation(task_id):
    """
    Returns geolocation information of task with specified ID

    :param task_id: task ID
    """
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    geolocation = db.geolocation.find_one({'_id': ObjectId(task['geolocation_id'])})

    return geolocation


def get_task_subresource(task_id, resource_name):
    """
    Returns subresource of task with specified task_id

    :param task_id: task ID
    :param resource_name: resource name
    """
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    analysis = db.analyses.find_one({'_id': ObjectId(task['analysis_id'])})

    if resource_name == 'options':
        resource = [analysis]
    else:
        resource = db[resource_name].find({'analysis_id': ObjectId(analysis['_id'])})

    tmp_dict = list()

    # Replaces url_ids with actual urls
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
