from flask import Blueprint
from flask_restful import Api
from webclient.api.controllers import tasks, jobs, schedules, useragents

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1.0')
api = Api(api_blueprint)

api.add_resource(tasks.TaskList, '/tasks/')
api.add_resource(tasks.Task, '/tasks/<task_id>')
api.add_resource(tasks.TasksByJob, '/jobs/<job_id>/tasks/')

api.add_resource(jobs.JobList, '/jobs/')
api.add_resource(jobs.Job, '/jobs/<job_id>')
api.add_resource(jobs.JobsBySchedule, '/schedules/<schedule_id>/jobs/')

api.add_resource(schedules.ScheduleList, '/schedules/')
api.add_resource(schedules.Schedule, '/schedules/<schedule_id>')

api.add_resource(useragents.UserAgentList, '/useragents/')
