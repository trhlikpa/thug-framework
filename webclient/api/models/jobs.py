import json
from flask import g
from bson import ObjectId
from webclient.api.models.schedules import create_schedule, get_schedule
from webclient.dbcontext import db
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.api.utils.celeryutils import normalize_job_states
from worker.tasks import execute_job, revoke_job


def get_jobs(args, schedule_id=None):
    """
    Returns list of jobs

    :param args: pagination and filtering arguments
    :param schedule_id: schedule ID
    """
    normalize_job_states()
    page, pagesize, sort, filter_args = parse_url_parameters(args)

    filter_fields = {}

    if schedule_id is not None:
        schedule = get_schedule(schedule_id)

        if not schedule:
            return list()

        previous_runs = schedule['previous_runs']
        filter_fields = {'_id': {'$in': previous_runs}}

    if filter_args:
        tmp_and = []
        tmp_or = []

        for filter_arg in filter_args:
            values = filter_arg['values']
            field = filter_arg['field']
            value = '|'.join(map(unicode, values))
            regex = {'$regex': '.*(' + value + ').*', '$options': 'ix'}

            if field == 'all':
                tmp_or.extend([{'url': regex},
                               {'name': regex},
                               {'useragent': regex},
                               {'_state': regex},
                               {'type': regex},
                               {'end_time': regex},
                               {'classification': regex}])
                break
            elif field in ['end_time', 'start_time', 'submit_time']:
                if len(values) == 2:
                    tmp_and.append({field: {'$gte': values[0], '$lte': values[1]}})
                else:
                    tmp_and.append({field: regex})
            elif field == 'mine':
                tmp_and.append({'submitter_id': g.user['email']})
            else:
                tmp_and.append({field: regex})

        if len(tmp_or) > 0:
            filter_fields['$or'] = tmp_or

        if len(tmp_and) > 0:
            filter_fields['$and'] = tmp_and

    jobs = get_paged_documents(db.jobs,
                               page=page,
                               pagesize=pagesize,
                               sort=sort,
                               filter_fields=filter_fields)

    json_string = json.dumps(jobs)
    return json_string


def get_job(job_id):
    """
    Returns job with job_id

    :param job_id: job ID
    """
    if not job_id or len(job_id) != 24:
        return None

    normalize_job_states()
    job = db.jobs.find_one({'_id': ObjectId(job_id)})

    return job


def create_job(data):
    """
    Creates job

    :param data: job parameters
    :return: job ID
    """
    url = data.get('url')

    if not url:
        raise AttributeError('URL is missing')

    job_name = data.get('name')

    if not job_name:
        raise AttributeError('Name is missing')

    submitter_id = data.get('submitter_id')

    if submitter_id is None:
        raise AttributeError('Submitter id is missing')

    job_type = data.get('type') or 'singleurl'
    user_agent = data.get('useragent') or 'winxpie60'
    crawler_time_limit = data.get('crawler_time_limit') or 600
    thug_time_limit = data.get('thug_time_limit') or 600

    eta = data.get('eta')
    cron = data.get('cron')
    interval = data.get('interval')
    max_run_count = data.get('max_run_count') or 100

    args = {
        'referer': data.get('referer'),
        'java': data.get('java'),
        'shockwave': data.get('shockwave'),
        'adobepdf': data.get('adobepdf'),
        'proxy': data.get('proxy'),
        'dom_events': data.get('dom_events'),
        'no_cache': bool(data.get('no_cache')),
        'web_tracking': bool(data.get('web_tracking')),
        'url_classifiers': data.get('url_classifiers'),
        'html_classifiers': data.get('html_classifiers'),
        'js_classifiers': data.get('js_classifiers'),
        'vb_classifiers': data.get('vb_classifiers'),
        'sample_classifiers': data.get('sample_classifiers'),
        'depth_limit': data.get('depth_limit') or 1,
        'only_internal': bool(data.get('only_internal')),
        'allowed_domains': data.get('allowed_domains'),
        'download_delay': data.get('download_delay') or 0,
        'randomize_download_delay': bool(data.get('randomize_download_delay')),
        'redirect_max_times': data.get('redirect_max_times') or 30,
        'robotstxt_obey': bool(data.get('robotstxt_obey'))
    }

    job_data = {
        '_state': 'PENDING',
        '_current_url': None,
        '_error': None,
        'type': job_type,
        'name': job_name,
        'url': url,
        'useragent': user_agent,
        'classification': None,
        'start_time': None,
        'end_time': None,
        'crawler_start_time': None,
        'crawler_end_time': None,
        'crawler_time_limit': crawler_time_limit,
        'thug_time_limit': thug_time_limit,
        'eta': eta,
        'submitter_id': submitter_id,
        'schedule_id': None,
        'args': args,
        'tasks': []
    }

    # Schedule job if cron or interval is present
    if cron or interval:
        create_schedule(task='worker.tasks.execute_job', name=job_name, submitter_id=submitter_id, args=[job_data],
                        max_run_count=max_run_count, run_after=eta, cron=cron, interval=interval)
        return None

    job_id = execute_job.apply(args=[job_data], task_id=str(ObjectId()))
    return job_id.result


def delete_job(job_id):
    """
    Deletes job with specified job_id

    :param job_id: job ID
    :return: True if successful, False otherwise
    """
    if not job_id or len(job_id) != 24:
        return None

    return revoke_job(job_id)


def update_job(job_id, data):
    """
    Updates job with specified job_id

    :param job_id: job ID
    :param data: fields to change
    :return: job ID
    """
    if not job_id or len(job_id) != 24:
        return None

    job_name = data.get('name')

    db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': {'name': job_name}})

    return job_id
