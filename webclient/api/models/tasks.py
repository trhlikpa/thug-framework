from webclient import config
from bson import ObjectId, json_util
from webclient.api.utils.pagination import get_paged_documents
from webclient.api.utils.celeryutil import normalize_state
from webclient.dbcontext import db
from worker.tasks import analyze_url


def qet_tasks(args):
    """
    Method queries tasks from database
    :param args:
    :return: list of tasks
    """
    normalize_state(db.tasks, float(config['THUG_TIMELIMIT']))
    json_string = get_paged_documents(db.tasks, args, collums={'_id': 1,
                                                               '_state': 1,
                                                               'thug': 1,
                                                               'url': 1,
                                                               'error': 1,
                                                               'start_time': 1,
                                                               'end_time': 1
                                                               })

    return json_string


def qet_task(task_id):
    """
    Method queries specified task from database
    :param task_id: task id
    :return: specified task
    """
    normalize_state(db.tasks, float(config['THUG_TIMELIMIT']))
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if task is None:
        return None

    return task


def create_task(data):
    """
    Method puts new task into thug worker queue
    :param data: input data
    :return: task id
    """
    json_data = {
        '_state': 'PENDING',
        'start_time': None,
        'end_time': None
    }

    oid = db.tasks.insert(json_data)

    input_data = {x: data[x] if x in data else ''
                  for x in ['useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy']}

    analyze_url.apply_async(args=[input_data], task_id=str(oid))
    return str(oid)


def delete_task(task_id):
    """
    Method revokes task
    :param task_id: task id
    """
    analyze_url.AsyncResult(task_id).revoke()
    result_db = db.tasks.delete_one({'_id': ObjectId(task_id)})

    if result_db.deleted_count > 0:
        return True

    return False
