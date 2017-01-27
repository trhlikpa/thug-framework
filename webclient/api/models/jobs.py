import json
from webclient.dbcontext import db
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.api.utils.celeryutils import normalize_job_states
from worker.tasks import execute_job, revoke_job


def get_jobs(args):
    normalize_job_states()
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    filter_fields = None

    if filter_arg:
        tmp = [{'url': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'name': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'useragent': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'_state': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'type': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'classification': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}}]

        filter_fields['$or'] = tmp

    d = get_paged_documents(db.jobs,
                            page=page,
                            pagesize=pagesize,
                            sort=sort,
                            collums=None,
                            filter_fields=filter_fields)

    json_string = json.dumps(d)
    return json_string


def get_job(job_id):
    normalize_job_states()
    job = db.jobs.find_one({'_id': job_id})

    return job


def create_job(data):
    job_type = data.get('type')
    job_name = data.get('name')
    submitter_id = data.get('submitter_id')
    crawler_time_limit = data.get('crawler_time_limit')
    thug_time_limit = data.get('thug_time_limit')
    url = data.get('url')
    user_agent = data.get('useragent')

    job_args = {x: data[x] if x in data else None for x in
                {
                    'referer',
                    'java',
                    'shockwave',
                    'adobepdf',
                    'proxy',
                    'dom_events',
                    'no_cache',
                    'web_tracking',
                    'url_classifiers',
                    'html_classifiers',
                    'js_classifiers',
                    'vb_classifiers',
                    'sample_classifiers',
                    'depth_limit',
                    'only_internal',
                    'allowed_domains',
                    'download_delay',
                    'randomize_download_delay',
                    'redirect_max_times',
                    'robotstxt_obey'
                }}

    job_id = execute_job.apply(args=[url, user_agent, submitter_id, job_name, job_type, job_args, crawler_time_limit,
                                     thug_time_limit])

    return job_id.result


def delete_job(job_id):
    revoke_job(job_id)
