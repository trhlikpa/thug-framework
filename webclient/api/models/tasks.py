import datetime
from uuid import uuid4
from webclient.dbcontext import db
from worker.tasks import analyze_url
from webclient import TIMEZONE


def qet_tasks():
    """
    Method queries tasks from database
    :return: list of tasks
    """
    query = db.tasks.find({}, {'url': 1,
                               'submit_time': 1,
                               '_id': 1,
                               '_state': 1,
                               'start_time': 1,
                               'end_time': 1
                               })

    if query.count() != 0:
        return query

    return list()


def qet_task(task_id):
    """
    Method queries specified task from database
    :param task_id: task id
    :return: specified task
    """
    query = db.tasks.find({'_id': task_id})

    if query.count() != 0:
        return query

    return None


def create_task(data):
    """
    Method puts new task into thug worker queue
    :param data: input data
    :return: task id
    """
    uuid = str(uuid4())

    json_data = {
        '_id': uuid,
        '_state': 'PENDING',
        'submit_time': datetime.datetime.now(TIMEZONE)
    }

    db.tasks.insert(json_data)

    input_data = {x: data[x] if x in data else ''
                  for x in ['useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy']}

    task = analyze_url.apply_async(args=[input_data], task_id=uuid)
    return task.id


def delete_task(task_id):
    """
    Method revokes task
    :param task_id: task id
    """
    analyze_url.AsyncResult(task_id).revoke(terminate=True)
    db.tasks.remove({'_id': task_id})


def get_taskinfo(task_id):
    """
    Helper method returns info about task
    :param task_id: task id
    :return: task state and info
    """
    task_result = analyze_url.AsyncResult(task_id)
    return task_result.state, task_result.info
