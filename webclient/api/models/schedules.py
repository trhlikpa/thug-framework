import json
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.dbcontext import db
from bson.objectid import ObjectId


def get_schedules(args):
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    filter_fields = None

    if filter_arg is not None:
        tmp = [{'name': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}}]
        filter_fields = {
            '$or': tmp
        }

    d = get_paged_documents(db.schedules,
                            page=page,
                            pagesize=pagesize,
                            sort=sort,
                            collums=None,
                            filter_fields=filter_fields)

    json_string = json.dumps(d)
    return json_string


def get_schedule(schedule_id):
    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

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
    input_data['args'][0]['classification'] = None

    if 'java' not in input_data['args'][0]:
        input_data['args'][0]['java'] = None

    if 'shockwave' not in input_data['args'][0]:
        input_data['args'][0]['shockwave'] = None

    if 'adobepdf' not in input_data['args'][0]:
        input_data['args'][0]['adobepdf'] = None

    if 'proxy' not in input_data['args'][0]:
        input_data['args'][0]['proxy'] = None

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
    result_db = db.schedules.delete_one({'_id': ObjectId(schedule_id)})

    if result_db.deleted_count > 0:
        return True

    return False


def pause_schedule(schedule_id):
    db.schedules.update_one({'_id': schedule_id}, {'$set': {'enabled': False}})
