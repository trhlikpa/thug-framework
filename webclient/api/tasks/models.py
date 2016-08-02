from uuid import uuid4
from webclient.dbcontext import db
from worker.tasks import analyze_url


def qet_tasks():
    query = db.tasks.find({}, {'url': 1, 'timestamp': 1, '_id': 1, '_state': 1})

    if query.count() != 0:
        return query

    return list()


def qet_task(task_id):
    query = db.tasks.find({'_id': task_id})

    if query.count() != 0:
        return query

    return None


def create_task(data):
    uuid = str(uuid4())

    json_data = {
        '_id': uuid,
        '_state': 'PENDING'
    }

    db.tasks.insert(json_data)

    input_data = {x: data[x] if x in data else ''
                  for x in ['useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy']}

    task = analyze_url.apply_async(args=[input_data], task_id=uuid)
    return task.id


def delete_task(task_id):
    analyze_url.AsyncResult(task_id).revoke(terminate=True)
    db.tasks.remove({'_id': task_id})


def get_taskinfo(task_id):
    task_result = analyze_url.AsyncResult(task_id)
    return task_result.state, task_result.info
