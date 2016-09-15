from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.jobs import get_job, get_jobs, create_job, delete_job


class Job(Resource):
    def get(self, job_id):
        job = None
        try:
            job = get_job(job_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

        response = Response(json_util.dumps({'job': job}), mimetype='application/json')
        return response

    def delete(self, job_id):
        result = None
        try:
            result = delete_job(job_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

        response = Response(json_util.dumps({'job': result}), mimetype='application/json')
        return response


class JobList(Resource):
    def post(self):
        parser = reqparse.RequestParser()

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
        parser.add_argument('crontab', type=str, help='Crontab job schedule', default=None)

        args = parser.parse_args()

        job_id = None
        try:
            job_id = create_job(args)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'job': job_id}),  mimetype='application/json')
        return response

    def get(self):
        jobs = None
        try:
            jobs = get_jobs()
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

        response = Response(json_util.dumps({'jobs': jobs}, default=json_util.default),
                            mimetype='application/json')
        return response
