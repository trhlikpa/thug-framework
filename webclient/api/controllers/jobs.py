from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.jobs import get_job, get_jobs, create_job, delete_job
from webclient.api.utils.decorators import login_required


class Job(Resource):
    @classmethod
    def get(cls, job_id):
        job = None
        try:
            job = get_job(job_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'job': job}), mimetype='application/json')
        return response

    @classmethod
    def delete(cls, job_id):
        result = None
        try:
            result = delete_job(job_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'job': result}), mimetype='application/json')
        return response


class JobList(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()

        # General params
        parser.add_argument('name', type=str, help='Name of the job', required=True)
        parser.add_argument('url', type=str, help='URL to analyze', required=True)
        parser.add_argument('useragent', type=str, help='Browser personality', required=True)
        parser.add_argument('type', type=str, help='Job type (singleurl or extensive)', required=True,
                            choices=['singleurl', 'extensive'])
        parser.add_argument('submitter_id', type=str, help='Submitter ID')

        # Thug params
        parser.add_argument('java', type=str, help='Java plugin version')
        parser.add_argument('shockwave', type=str, help='Shockwave Flash plugin version')
        parser.add_argument('adobepdf', type=str, help='Adobe Acrobat Reader version')
        parser.add_argument('proxy', type=str, help='Proxy format: scheme://[username:password@]host:port')
        parser.add_argument('thug_time_limit', type=int, help='Time limit for thug execution')

        # Crawler params
        parser.add_argument('depth_limit', type=int, help='Webcrawler depth limit', default=0)
        parser.add_argument('download_delay', type=int, help='Webcrawler download delay', default=0)
        parser.add_argument('randomize_download_delay', type=bool, help='Randomize crawler depth limit', default=False)
        parser.add_argument('redirect_max_times', type=int, help='Webcrawler max redirects', default=30)
        parser.add_argument('robotstxt_obey', type=bool, help='Should webcrawler obey robotstxt rules', default=False)
        parser.add_argument('only_internal', type=bool, help='Crawl only initial domain', default=True)
        parser.add_argument('crawler_time_limit', type=int, help='Time limit for crawler', default=3600)
        parser.add_argument('allowed_domains', type=list, help='List of allowed domains')

        args = parser.parse_args()

        job_id = None

        try:
            job_id = create_job(args)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'job': job_id}), mimetype='application/json')
        return response

    @classmethod
    def get(cls):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        jobs = None
        try:
            jobs = get_jobs(args)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(jobs, mimetype='application/json')
        return response


class JobsBySchedule(Resource):
    @classmethod
    def get(cls, schedule_id):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        jobs = None
        try:
            jobs = get_jobs(args, schedule_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(jobs, mimetype='application/json')
        return response
