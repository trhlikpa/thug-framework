import datetime
from uuid import uuid4
from webclient.dbcontext import db
from worker.tasks import analyze_url
from webclient import config


def normalize_state(task):
    if 'start_time' in task:
        start_time = task['start_time']
        now_time = datetime.datetime.utcnow()
        limit_time = start_time + datetime.timedelta(seconds=float(config['THUG_TIMELIMIT']))
        if now_time > limit_time:
            _, info = get_taskinfo(task['_id'])
            task['_state'] = 'FAILURE'
            task['error'] = str(info)
            db.tasks.update_one({},  {'$set': task})


def qet_tasks():
    """
    Method queries tasks from database
    :return: list of tasks
    """
    query = list(db.tasks.find({}, {'url': 1,
                                    'submit_time': 1,
                                    '_id': 1,
                                    '_state': 1,
                                    'start_time': 1,
                                    'end_time': 1
                                    }, modifiers={"$snapshot": True}))

    if query.count != 0:
        for task in query:
            if task['_state'] == 'STARTED':
                normalize_state(task)

        return query

    return list()


def qet_task(task_id):
    """
    Method queries specified task from database
    :param task_id: task id
    :return: specified task
    """
    task = db.tasks.find_one({'_id': task_id})

    if task is None:
        return None

    if task['_state'] == 'STARTED':
        normalize_state(task)

    return task


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
        'submit_time': datetime.datetime.utcnow()
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
    analyze_url.AsyncResult(task_id).revoke()
    result_db = db.tasks.delete_one({'_id': task_id})
    result_worker, _ = get_taskinfo(task_id)

    if result_db.deleted_count > 0:
        return True

    return False


def get_taskinfo(task_id):
    """
    Helper method returns info about task
    :param task_id: task id
    :return: task state and info
    """
    task_result = analyze_url.AsyncResult(task_id)
    return task_result.state, task_result.info
