from bson import json_util
from flask import Response, g
from flask_restful import Resource, reqparse
from webclient.api.models.jobs import get_job, get_jobs, create_job, delete_job, update_job
from webclient.api.utils.decorators import handle_errors, login_required, validate_user


class Job(Resource):
    """
    Resource representing '/api/v1.0/jobs/<job_id>/' api route

    available methods: GET, DELETE, PUT
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls, job_id):
        """
        Returns Job with specified job_id

        GET /api/v1.0/jobs/<job_id>/

        URL parameters:
            :job_id: Job ID

        :return: JSON encoded job document; null if not found
        """
        job = get_job(job_id)
        response = Response(json_util.dumps({'job': job}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    @validate_user
    @login_required
    def delete(cls, job_id):
        """
        Deletes Job with specified job_id

        DELETE /api/v1.0/jobs/<job_id>/

        URL parameters:
            :job_id: Job ID

        :return: True if removed, False otherwise
        """
        result = delete_job(job_id)
        response = Response(json_util.dumps({'job': result}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    @validate_user
    @login_required
    def put(cls, job_id):
        """
        Updates Job with specified job_id

        PUT /api/v1.0/jobs/<job_id>/

        URL parameters:
            :job_id: Job ID

        Request body parameters:
            :name: New name

        :return: Job ID
        """
        parser = reqparse.RequestParser()

        parser.add_argument('name', type=str, help='New name')

        args = parser.parse_args()

        job = update_job(job_id, args)
        response = Response(json_util.dumps({'job': job}), mimetype='application/json')

        return response


class JobList(Resource):
    """
    Resource representing '/api/v1.0/jobs/' api route

    available methods: GET, POST
    """
    @classmethod
    @handle_errors
    @login_required
    def post(cls, *args, **kwargs):
        """
        Creates new job

        POST /api/v1.0/jobs/

        Request body parameters:

        name, url, useragent, type, eta, max_run_count, cron, interval,
        referer, java, shockwave, adobepdf, proxy, thug_time_limit, dom_events, no_cache, web_tracking,
        url_classifiers, html_classifiers, js_classifiers, sample_classifiers, depth_limit, download_delay,
        randomize_download_delay, redirect_max_times, robotstxt_obey, only_internal, crawler_time_limit,
        allowed_domains

        :return: Job ID
        """
        parser = reqparse.RequestParser()

        # General params
        parser.add_argument('name', type=unicode, help='Name of the job', required=True)
        parser.add_argument('url', type=str, help='URL to analyze', required=True)
        parser.add_argument('useragent', type=str, help='Browser personality', required=True)
        parser.add_argument('type', type=str, help='Job type (singleurl or extensive)', required=True,
                            choices=['singleurl', 'extensive'])

        # Schedule params
        parser.add_argument('eta', type=str, help='Estimated time of arival; ISO 8601 string format')
        parser.add_argument('max_run_count', type=int, help='Number of job runs')
        parser.add_argument('cron', type=dict, help='Schedule in cron format')
        parser.add_argument('interval', type=dict, help='Schedule defined as intervals')

        # Thug params
        parser.add_argument('referer', type=str, help='HTML referer')
        parser.add_argument('java', type=str, help='Java plugin version')
        parser.add_argument('shockwave', type=str, help='Shockwave Flash plugin version')
        parser.add_argument('adobepdf', type=str, help='Adobe Acrobat Reader version')
        parser.add_argument('proxy', type=str, help='Proxy format: scheme://[username:password@]host:port')
        parser.add_argument('thug_time_limit', type=int, help='Time limit for thug execution')
        parser.add_argument('dom_events', type=str, help='DOM event separated by comma')
        parser.add_argument('no_cache', type=bool, help='Disable local web cache')
        parser.add_argument('web_tracking', type=bool, help='Enable web tracking inspection')
        parser.add_argument('url_classifiers', type=list, location='json', help='URL classifiers')
        parser.add_argument('html_classifiers', type=list, location='json', help='HTML classifiers')
        parser.add_argument('js_classifiers', type=list, location='json', help='JS classifiers')
        parser.add_argument('vb_classifiers', type=list, location='json', help='VB classifiers')
        parser.add_argument('sample_classifiers', type=list, location='json', help='Sample classifiers')

        # Crawler params
        parser.add_argument('depth_limit', type=int, help='Webcrawler depth limit')
        parser.add_argument('download_delay', type=int, help='Webcrawler download delay')
        parser.add_argument('randomize_download_delay', type=bool, help='Randomize crawler depth limit')
        parser.add_argument('redirect_max_times', type=int, help='Webcrawler max redirects')
        parser.add_argument('robotstxt_obey', type=bool, help='Should webcrawler obey robotstxt rules')
        parser.add_argument('only_internal', type=bool, help='Crawl only initial domain')
        parser.add_argument('crawler_time_limit', type=int, help='Time limit for crawler')
        parser.add_argument('allowed_domains', type=list, location='json', help='List of allowed domains')

        args = parser.parse_args()
        args['submitter_id'] = g.user['email']

        job_id = create_job(args)
        response = Response(json_util.dumps({'job': job_id}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns list of jobs

        GET /api/v1.0/jobs/

        Query string arguments:

        :sort: field and direction to sort on, default: '_id|1'
        :page: page to show
        :per_page: entries per page
        :filter: phrase to filter

        :return: list of jobs
        """
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=unicode, location='args')

        args = parser.parse_args()

        jobs = get_jobs(args)
        response = Response(jobs, mimetype='application/json')

        return response


class JobsBySchedule(Resource):
    """
    Resource representing '/schedules/<schedule_id>/jobs/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls, schedule_id):
        """
        Returns list of jobs with specified schedule_id

        GET /schedules/<schedule_id>/jobs/

        URL parameters:

        :schedule_id: schedule ID

        Query string arguments:

        :sort: field and direction to sort on, default: '_id|1'
        :page: page to show
        :per_page: entries per page
        :filter: phrase to filter

        :return: list of jobs
        """
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=unicode, location='args')

        args = parser.parse_args()

        jobs = get_jobs(args, schedule_id)
        response = Response(jobs, mimetype='application/json')

        return response
