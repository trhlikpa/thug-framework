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
    @login_required
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
    @login_required
    def post(cls):
        parser = reqparse.RequestParser()

        parser.add_argument('name', type=str, help='Name of the job', required=True)
        parser.add_argument('url', type=str, help='URL to analyze by thug', required=True)
        parser.add_argument('useragent', type=str, help='Browser personality', required=True)
        parser.add_argument('type', type=str, help='Job type (singleurl or extensive)', required=True,
                            choices=['singleurl', 'extensive'])
        parser.add_argument('java', type=str, help='Java plugin version')
        parser.add_argument('shockwave', type=str, help='Shockwave Flash plugin version')
        parser.add_argument('adobepdf', type=str, help='Adobe Acrobat Reader version')
        parser.add_argument('proxy', type=str, help='Proxy format: scheme://[username:password@]host:port')
        parser.add_argument('depth', type=str, help='Webcrawler depth')
        parser.add_argument('only_internal', type=str, help='Crawl only initial domain')

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
