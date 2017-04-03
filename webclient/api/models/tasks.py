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
            value = '|'.join(map(unicode, values))
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
    if not task_id or len(task_id) != 24:
        return None

    normalize_task_states()
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    return task


def delete_task(task_id):
    """
    Deletes task with specified task_id

    :param task_id: task ID
    :return: True if successful, False otherwise
    """
    if not task_id or len(task_id) != 24:
        return None

    return revoke_task(task_id)
