import json
from datetime import datetime
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.dbcontext import db
from bson.objectid import ObjectId


def get_schedules(args):
    """
    Returns list of schedules

    :param args: pagination and filtering arguments
    """
    page, pagesize, sort, filter_args = parse_url_parameters(args)

    filter_fields = {}

    if filter_args:
        tmp = []

        for filter_arg in filter_args:
            values = filter_arg['values']
            field = filter_arg['field']
            value = '|'.join(map(unicode, values))
            regex = {'$regex': '.*(' + value + ').*', '$options': 'ix'}

            if field == 'all':
                tmp.extend([{'name': regex},
                            {'enabled': regex}])
                break

        if len(tmp) > 0:
            filter_fields['$or'] = tmp

    schedules = get_paged_documents(db.schedules,
                                    page=page,
                                    pagesize=pagesize,
                                    sort=sort,
                                    filter_fields=filter_fields)

    # Convert unix timestamp to ISO 8601 string
    for schedule in schedules['data']:
        if schedule['last_run_at']:
            schedule['last_run_at'] = datetime.fromtimestamp(schedule['last_run_at']['$date'] / 1000.0).isoformat()

    json_string = json.dumps(schedules)
    return json_string


def get_schedule(schedule_id):
    """
    Returns schedule with specified schedule_id

    :param schedule_id: Schedule ID
    """
    if not schedule_id or len(schedule_id) != 24:
        return None

    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    # Convert python datetime object to ISO 8601 string
    if schedule['last_run_at']:
        schedule['last_run_at'] = schedule['last_run_at'].isoformat()

    return schedule


def create_schedule(task, name, max_run_count, run_after, cron=None, interval=None, args=None, kwargs=None, opt=None):
    """
    Creates new schedule

    :param task: celery task
    :param name: schedule name
    :param max_run_count: maximum number of celery task iterations
    :param run_after: run first celery task after
    :param cron: crontab type schedule
    :param interval: interval type schedule
    :param args: task arguments
    :param kwargs: task key word arguments
    :param opt: task options
    :return: schedule ID
    """
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
    """
    Deletes schedule with specified schedule_id

    :param schedule_id: schedule ID
    :return: True if successful, False otherwise
    """
    if not schedule_id or len(schedule_id) != 24:
        return None

    schedule = db.schedules.find_one({'_id': ObjectId(schedule_id)})

    for job_id in schedule['previous_runs']:
        db.jobs.update_one({'_id': job_id}, {'$set': {'schedule_id': None}})

    result_db = db.schedules.delete_one({'_id': ObjectId(schedule_id)})

    if result_db.deleted_count > 0:
        return True

    return False


def update_schedule(schedule_id, data):
    """
    Updates schedule with specified schedule_id

    :param schedule_id: schedule ID
    :param data: field to update
    :return: schedule ID
    """
    if not schedule_id or len(schedule_id) != 24:
        return None

    enabled = data.get('enabled', False)
    schedule_name = data.get('name')

    db.schedules.update_one({'_id': ObjectId(schedule_id)}, {'$set': {'enabled': enabled, 'name': schedule_name}})

    return schedule_id
