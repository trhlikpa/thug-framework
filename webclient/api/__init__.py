from flask import Blueprint
from flask_restful import Api
from webclient.api.controllers import tasks, jobs

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1.0')
api = Api(api_blueprint)

api.add_resource(tasks.TaskList, '/tasks/')
api.add_resource(tasks.Task, '/tasks/<task_id>')

api.add_resource(jobs.JobList, '/jobs/')
api.add_resource(jobs.Job, '/job/<job_id>')
