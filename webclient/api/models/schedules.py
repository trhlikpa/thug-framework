from webclient.api.utils.pagination import get_paged_documents
from webclient.dbcontext import db
from bson.objectid import ObjectId
from bson import json_util


def get_schedules(args):
    json_string = get_paged_documents(db.schedules, args)
    return json_string


def get_schedule(schedule_id):
    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    if schedule is None:
        return None

    return schedule


def create_schedule(data):
    input_data = {x: data[x] if x in data else '' for x in
                  ['name', 'crontab', 'args', 'kwargs', 'task']}

    if 'url' not in input_data['args'][0] or 'type' not in input_data['args'][0] or 'useragent' not in \
            input_data['args'][0]:
        raise ValueError('Job parameters error during schedule creation')

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
