from bson import json_util
from flask import Response
from flask_restful import Resource, reqparse
from webclient.api.models.tasks import get_task, delete_task, get_tasks, get_task_subresource
from webclient.api.utils.decorators import handle_errors


class Task(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        task = get_task(task_id)
        response = Response(json_util.dumps({'task': task}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    def delete(cls, task_id):
        delete_task(task_id)
        response = Response(json_util.dumps({'task': None}), mimetype='application/json')

        return response


class TaskList(Resource):
    @classmethod
    @handle_errors
    def get(cls):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        tasks = get_tasks(args)
        response = Response(tasks, mimetype='application/json')

        return response


class TasksByJob(Resource):
    @classmethod
    @handle_errors
    def get(cls, job_id):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        tasks = get_tasks(args, job_id)
        response = Response(tasks, mimetype='application/json')

        return response


def get_subresource(task_id, resource_name):
    resource = get_task_subresource(task_id, resource_name)
    response = Response(json_util.dumps({resource_name: resource}), mimetype='application/json')

    return response


class Options(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'options')


class Connections(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'connections')


class Locations(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'locations')


class Samples(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'samples')


class Exploits(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'exploits')


class Classifiers(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'classifiers')


class Codes(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'codes')


class Behaviours(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'behaviours')


class Graphs(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'graphs')


class Virustotal(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'virustotal')


class Honeyagent(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'honeyagent')


class Androguard(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'androguard')


class Peepdf(Resource):
    @classmethod
    @handle_errors
    def get(cls, task_id):
        return get_subresource(task_id, 'peepdf')
