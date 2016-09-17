from webclient.api.utils.pagination import get_paged_documents
from webclient.dbcontext import db
from bson.objectid import ObjectId
from bson import json_util


def get_schedules(args):
    query, links = get_paged_documents(db.schedules, args)

    if links is None:
        return json_util.dumps({'data': query}, default=json_util.default)
    else:
        return json_util.dumps({'data': query, 'links': links}, default=json_util.default)


def get_schedule(schedule_id):
    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    if schedule is None:
        return None

    return schedule


def create_schedule(data):
    input_data = {x: data[x] if x in data else '' for x in
                  ['name', 'crontab', 'args', 'kwargs', 'task']}

    oid = ObjectId()

    input_data['args'][0]['schedule_id'] = str(oid)
    input_data['args'][0]['start_time'] = None
    input_data['args'][0]['end_time'] = None

    json_data = {
        '_id': oid,
        '_cls': 'PeriodicTask',
        'enabled': True,
        'previous_runs': []
    }

    json_data.update(input_data)

    db.schedules.insert(json_data)

    return str(oid)


def delete_schedule(schedule_id):
    pass


def update_schedule(schedule_id, **params):
    pass


def pause_schedule(schedule_id):
    pass
