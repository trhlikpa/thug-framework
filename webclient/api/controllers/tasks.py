from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.tasks import qet_task, delete_task, qet_tasks, create_task


class Task(Resource):
    def get(self, task_id):
        try:
            tasks = qet_task(task_id)

            response = Response(json_util.dumps({'tasks': tasks}, default=json_util.default),
                                mimetype='application/json')

            return response
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

    def delete(self, task_id):
        try:
            result = delete_task(task_id)

            response = Response(json_util.dumps({'task': result}),
                                mimetype='application/json')

            return response
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)


class TaskList(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('url', type=str, help='URL to analyze by thug')
            parser.add_argument('useragent', type=str, help='Browser personality')
            parser.add_argument('java', type=str, help='Java plugin version')
            parser.add_argument('shockwave', type=str, help='Shockwave Flash plugin version')
            parser.add_argument('adobepdf', type=str, help='Adobe Acrobat Reader version')
            parser.add_argument('proxy', type=str, help='Proxy format: scheme://[username:password@]host:port')

            args = parser.parse_args()
            task_id = create_task(args)

            response = Response(json_util.dumps({'task': task_id}),
                                mimetype='application/json')

            return response
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

    def get(self):
        try:
            tasks = qet_tasks()

            response = Response(json_util.dumps({'tasks': tasks}, default=json_util.default),
                                mimetype='application/json')

            return response
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)
