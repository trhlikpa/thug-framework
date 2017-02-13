import json
from datetime import datetime
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.dbcontext import db
from bson.objectid import ObjectId


def get_schedules(args):
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    schedules = get_paged_documents(db.schedules,
                                    page=page,
                                    pagesize=pagesize,
                                    sort=sort,
                                    collums=None)

    for schedule in schedules['data']:
        if schedule['last_run_at']:
            schedule['last_run_at'] = datetime.fromtimestamp(schedule['last_run_at']['$date'] / 1000.0).isoformat()

    json_string = json.dumps(schedules)
    return json_string


def get_schedule(schedule_id):
    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    if schedule['last_run_at']:
        schedule['last_run_at'] = schedule['last_run_at'].isoformat()

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


def update_schedule(schedule_id, data):
    enabled = data.get('enabled', False)
    schedule_name = data.get('name')

    db.schedules.update_one({'_id': ObjectId(schedule_id)}, {'$set': {'enabled': enabled, 'name': schedule_name}})

    return schedule_id
