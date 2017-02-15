from flask import Blueprint
from flask_restful import Api
from webclient.api.controllers import tasks, jobs, schedules, useragents, auth

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1.0')
api = Api(api_blueprint)

# Tasks
api.add_resource(tasks.TaskList, '/tasks/')
api.add_resource(tasks.Task, '/tasks/<task_id>/')
api.add_resource(tasks.TasksByJob, '/jobs/<job_id>/tasks/')

# Task subresources
api.add_resource(tasks.Options, '/tasks/<task_id>/options/')
api.add_resource(tasks.Connections, '/tasks/<task_id>/connections/')
api.add_resource(tasks.Locations, '/tasks/<task_id>/locations/')
api.add_resource(tasks.Samples, '/tasks/<task_id>/samples/')
api.add_resource(tasks.Exploits, '/tasks/<task_id>/exploits/')
api.add_resource(tasks.Classifiers, '/tasks/<task_id>/classifiers/')
api.add_resource(tasks.Codes, '/tasks/<task_id>/codes/')
api.add_resource(tasks.Behaviours, '/tasks/<task_id>/behaviours/')
api.add_resource(tasks.Certificates, '/tasks/<task_id>/certificates/')
api.add_resource(tasks.Graphs, '/tasks/<task_id>/graphs/')
api.add_resource(tasks.Virustotal, '/tasks/<task_id>/virustotal/')
api.add_resource(tasks.Honeyagent, '/tasks/<task_id>/honeyagent/')
api.add_resource(tasks.Androguard, '/tasks/<task_id>/androguard/')
api.add_resource(tasks.Peepdf, '/tasks/<task_id>/peepdf/')
api.add_resource(tasks.Geolocation, '/tasks/<task_id>/geolocation/')

# Jobs
api.add_resource(jobs.JobList, '/jobs/')
api.add_resource(jobs.Job, '/jobs/<job_id>/')
api.add_resource(jobs.JobsBySchedule, '/schedules/<schedule_id>/jobs/')

# Schedules
api.add_resource(schedules.ScheduleList, '/schedules/')
api.add_resource(schedules.Schedule, '/schedules/<schedule_id>/')

# User agents
api.add_resource(useragents.UserAgentList, '/useragents/')

# Authentication
api.add_resource(auth.Login, '/auth/login/')
api.add_resource(auth.Register, '/auth/register/')
