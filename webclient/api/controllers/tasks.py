from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.tasks import get_task, delete_task, get_tasks, create_task
from webclient.api.utils.decorators import login_required


class Task(Resource):
    @classmethod
    def get(cls, task_id):
        task = None
        try:
            task = get_task(task_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'task': task}), mimetype='application/json')
        return response

    @classmethod
    @login_required
    def delete(cls, task_id):
        result = None
        try:
            result = delete_task(task_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'task': result}), mimetype='application/json')
        return response


class TaskList(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()

        parser.add_argument('url', type=str, help='URL to analyze by thug', required=True)
        parser.add_argument('useragent', type=str, help='Browser personality', required=True)
        parser.add_argument('java', type=str, help='Java plugin version')
        parser.add_argument('shockwave', type=str, help='Shockwave Flash plugin version')
        parser.add_argument('adobepdf', type=str, help='Adobe Acrobat Reader version')
        parser.add_argument('proxy', type=str, help='Proxy format: scheme://[username:password@]host:port')

        args = parser.parse_args()

        task_id = None
        try:
            task_id = create_task(args)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(json_util.dumps({'task': task_id}), mimetype='application/json')
        return response

    @classmethod
    def get(cls):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        tasks = None
        try:
            tasks = get_tasks(args)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(tasks, mimetype='application/json')
        return response


class TasksByJob(Resource):
    @classmethod
    def get(cls, job_id):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        tasks = None
        try:
            tasks = get_tasks(args, job_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % str(error))

        response = Response(tasks, mimetype='application/json')
        return response
