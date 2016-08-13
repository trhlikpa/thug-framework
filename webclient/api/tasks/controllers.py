from bson import json_util
from flask import Blueprint, abort, jsonify, request, Response
from webclient.api.tasks.models import qet_tasks, qet_task, create_task, delete_task

# Register task blueprint
tasks_blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_blueprint.route('/', methods=['GET'])
def get_tasks_controller():
    """
    :return: json collection with every task
    """
    tasks = qet_tasks()

    response = Response(json_util.dumps({'tasks': tasks}, default=json_util.default),
                        mimetype='application/json')

    return response


@tasks_blueprint.route('/<task_id>', methods=['GET'])
def get_task_controller(task_id):
    """
    :param task_id: task id
    :return: json collection of specified task
    """
    task = qet_task(task_id)

    if task is None:
        abort(400)

    response = Response(json_util.dumps({'task': task}, default=json_util.default),
                        mimetype='application/json')

    return response


@tasks_blueprint.route('/', methods=['POST'])
def create_task_controller():
    """
    :return: Newly created task id
    """
    if not request.json or 'url' not in request.json:
        abort(400)

    task_id = create_task(request.json)

    return jsonify({'task': task_id}), 201


@tasks_blueprint.route('/<task_id>', methods=['DELETE'])
def delete_task_controller(task_id):
    """
    :param task_id: task id to delete
    """
    delete_task(task_id)
    return jsonify(None)
