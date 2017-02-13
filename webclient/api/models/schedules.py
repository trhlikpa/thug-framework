import json
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.dbcontext import db
from bson.objectid import ObjectId


def get_schedules(args):
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    d = get_paged_documents(db.schedules,
                            page=page,
                            pagesize=pagesize,
                            sort=sort,
                            collums=None)

    json_string = json.dumps(d)
    return json_string


def get_schedule(schedule_id):
    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    return schedule


def create_schedule(task, name, max_run_count, run_after, cron=None, interval=None, args=None, kwargs=None, opt=None):
    schedule_id = ObjectId()

    args[0]['schedule_id'] = str(schedule_id)

    schedule = {
        '_id': schedule_id,
        'task': task,
        'name': name,
        'enabled': True,
        'args': args,
        'kwargs': kwargs,
        'max_run_count': max_run_count,
        'run_after': run_after,
        'total_run_count': 0,
        'last_run_at': None,
        'cron': cron,
        'interval': interval,
        'options': opt,
        'previous_runs': []
    }

    db.schedules.insert_one(schedule)

    return schedule_id


def delete_schedule(schedule_id):
    result_db = db.schedules.delete_one({'_id': ObjectId(schedule_id)})

    if result_db.deleted_count > 0:
        return True

    return False


def pause_schedule(schedule_id):
    db.schedules.update_one({'_id': schedule_id}, {'$set': {'enabled': False}})
