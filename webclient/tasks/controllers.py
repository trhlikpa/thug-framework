from flask import Blueprint, abort, jsonify, request
from webclient.tasks.models import qet_tasks, qet_task, create_task, delete_task

tasks_blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_blueprint.route('/', methods=['GET'])
def get_tasks_controller():
    tasks = qet_tasks()

    if tasks is None:
        abort(404)

    return jsonify({'tasks': tasks})


@tasks_blueprint.route('/<task_id>', methods=['GET'])
def get_task_controller(task_id):
    task = qet_task(task_id)

    if task is None:
        abort(404)

    return jsonify({'task': task})


@tasks_blueprint.route('/', methods=['POST'])
def create_task_controller():
    if not request.json or 'url' not in request.json:
        abort(400)

    task_id = create_task(request.json)

    return jsonify({'task': task_id}), 201


@tasks_blueprint.route('/<task_id>', methods=['DELETE'])
def delete_task_controller(task_id):
    delete_task(task_id)
    return jsonify({'task': True})
