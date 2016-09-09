import datetime
from webclient.dbcontext import db
from bson.objectid import ObjectId


def get_schedules():
    query = db.schedules.find()

    if query.count() != 0:
        return query

    return list()


def get_schedule(schedule_id):
    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    if schedule is None:
        return None

    return schedule


def create_schedule(data):
    input_data = {x: data[x] if x in data else '' for x in
                  ['crontab', 'args', 'kwargs', 'task']}

    name = input_data['task'] + ':' + str(datetime.datetime.utcnow())

    json_data = {
        '_cls': 'PeriodicTask',
        'enabled': True,
        'name': name,
        'previous_runs': []
    }

    json_data.update(input_data)

    oid = db.schedules.insert(json_data)

    return oid


def delete_schedule(schedule_id):
    pass


def update_schedule(schedule_id, **params):
    pass


def pause_schedule(schedule_id):
    pass
