from flask import Blueprint
from flask_restful import Api
from webclient.api.controllers import tasks

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1.0')
api = Api(api_blueprint)

api.add_resource(tasks.TaskList, '/tasks/')
api.add_resource(tasks.Task, '/tasks/<task_id>')
