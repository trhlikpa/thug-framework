from bson import json_util
from flask import Response, abort, g
from flask_restful import Resource, reqparse
from webapp.api.models.tasks import get_task, delete_task, get_tasks
from webapp.api.models.tasksubresources import get_task_subresource, get_task_geolocation
from webapp.api.utils.decorators import handle_errors, login_required


def task_belongs_to_user(task_id):
    """
    Checks if task belongs to a specified user

    :param task_id: task ID
    """
    task = get_task(task_id)

    if not task:
        abort(404, message='Task not found')

    if not g.user or not g.user['email']:
        abort(401, message='Invalid user ID')

    if g.user['email'] != task['submitter_id']:
        abort(401, message='You cannot modify this resource')


class Task(Resource):
    """
    Resource representing '/api/v1.0/tasks/<task_id>/' api route

    available methods: GET, DELETE
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns Task with specified task_id

        GET /api/v1.0/tasks/<task_id>/

        URL parameters:
            :task_id: Task ID

        :return: JSON encoded task document; null if not found
        """
        task = get_task(task_id)
        response = Response(json_util.dumps({'task': task}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    @login_required
    def delete(cls, task_id):
        """
        Deletes Task with specified task_id

        DELETE /api/v1.0/tasks/<task_id>/

        URL parameters:
            :task_id: Task ID

        :return: True if removed, False otherwise
        """
        result = delete_task(task_id)
        response = Response(json_util.dumps({'task': result}), mimetype='application/json')

        return response


class TaskList(Resource):
    """
    Resource representing '/api/v1.0/tasks/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns list of tasks

        GET /api/v1.0/tasks/

        Query string arguments:

        :sort: field and direction to sort on, default: '_id|1'
        :page: page to show
        :per_page: entries per page
        :filter: phrase to filter

        :return: list of tasks
        """
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=unicode, location='args')

        args = parser.parse_args()

        tasks = get_tasks(args)
        response = Response(tasks, mimetype='application/json')

        return response


class TasksByJob(Resource):
    """
    Resource representing '/jobs/<job_id>/tasks/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, job_id):
        """
        Returns list of tasks with specified job_id

        GET /jobs/<job_id>/tasks/

        URL parameters:

        :job_id: job ID

        Query string arguments:

        :sort: field and direction to sort on, default: '_id|1'
        :page: page to show
        :per_page: entries per page
        :filter: phrase to filter

        :return: list of tasks
        """
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=unicode, location='args')

        args = parser.parse_args()

        tasks = get_tasks(args, job_id)
        response = Response(tasks, mimetype='application/json')

        return response


def get_subresource(task_id, resource_name):
    """
    Returns task subresource

    :param task_id: task ID
    :param resource_name: name of task subresource
    """
    resource = get_task_subresource(resource_name, task_id)
    response = Response(json_util.dumps({resource_name: resource}), mimetype='application/json')

    return response


class OptionsByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/options/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns options

        GET /tasks/<task_id>/options/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'options')


class ConnectionsByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/connections/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns connections

        GET /tasks/<task_id>/connections/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'connections')


class LocationsByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/locations/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns locations

        GET /tasks/<task_id>/locations/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'locations')


class SamplesByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/samples/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns samples

        GET /tasks/<task_id>/samples/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'samples')


class ExploitsByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/exploits/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns exploits

        GET /tasks/<task_id>/exploits/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'exploits')


class ClassifiersByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/classifiers/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns classifiers

        GET /tasks/<task_id>/classifiers/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'classifiers')


class CodesByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/codes/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns codes

        GET /tasks/<task_id>/codes/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'codes')


class BehaviorsByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/behaviors/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns behaviors

        GET /tasks/<task_id>/behaviors/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'behaviors')


class CertificatesByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/certificates/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns certificates

        GET /tasks/<task_id>/certificates/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'certificates')


class GraphsByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/graphs/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns graphs

        GET /tasks/<task_id>/graphs/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'graphs')


class VirustotalByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/virustotal/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns virustotal document

        GET /tasks/<task_id>/virustotal/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'virustotal')


class HoneyagentByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/honeyagent/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns honeyagent document

        GET /tasks/<task_id>/honeyagent/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'honeyagent')


class AndroguardByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/androguard/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns androguard document

        GET /tasks/<task_id>/androguard/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'androguard')


class PeepdfByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/peepdf/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns peepdf document

        GET /tasks/<task_id>/peepdf/

        URL parameters:

        :task_id: task ID
        """
        return get_subresource(task_id, 'peepdf')


class GeolocationByTask(Resource):
    """
    Resource representing '/tasks/<task_id>/geolocation/' api route

    available methods: GET
    """

    @classmethod
    @handle_errors
    @login_required
    def get(cls, task_id):
        """
        Returns geolocation

        GET /tasks/<task_id>/geolocation/

        URL parameters:

        :task_id: task ID
        """
        geolocation = get_task_geolocation(task_id)
        response = Response(json_util.dumps({'geolocation': geolocation}), mimetype='application/json')

        return response
