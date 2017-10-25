from flask import Blueprint
from flask_restful import Api
from webapp.api.controllers import tasks, jobs, schedules, useragents, domevents, auth, plugins, tasksubresources

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1.0')
api = Api(api_blueprint)

# Tasks
api.add_resource(tasks.TaskList, '/tasks/')
api.add_resource(tasks.Task, '/tasks/<task_id>/')
api.add_resource(tasks.TasksByJob, '/jobs/<job_id>/tasks/')

# Task subresources
api.add_resource(tasksubresources.Urls, '/urls/')
api.add_resource(tasksubresources.Connections, '/connections/')
api.add_resource(tasksubresources.Locations, '/locations/')
api.add_resource(tasksubresources.Samples, '/samples/')
api.add_resource(tasksubresources.Exploits, '/exploits/')
api.add_resource(tasksubresources.Behaviors, '/behaviors/')

# Task subresources
api.add_resource(tasks.OptionsByTask, '/tasks/<task_id>/options/')
api.add_resource(tasks.ConnectionsByTask, '/tasks/<task_id>/connections/')
api.add_resource(tasks.LocationsByTask, '/tasks/<task_id>/locations/')
api.add_resource(tasks.SamplesByTask, '/tasks/<task_id>/samples/')
api.add_resource(tasks.ExploitsByTask, '/tasks/<task_id>/exploits/')
api.add_resource(tasks.ClassifiersByTask, '/tasks/<task_id>/classifiers/')
api.add_resource(tasks.CodesByTask, '/tasks/<task_id>/codes/')
api.add_resource(tasks.BehaviorsByTask, '/tasks/<task_id>/behaviors/')
api.add_resource(tasks.BehaviorsWithCode, '/tasks/<task_id>/behaviors/<behavior_id>/')
api.add_resource(tasks.CertificatesByTask, '/tasks/<task_id>/certificates/')
api.add_resource(tasks.GraphsByTask, '/tasks/<task_id>/graphs/')
api.add_resource(tasks.VirustotalByTask, '/tasks/<task_id>/virustotal/')
api.add_resource(tasks.HoneyagentByTask, '/tasks/<task_id>/honeyagent/')
api.add_resource(tasks.AndroguardByTask, '/tasks/<task_id>/androguard/')
api.add_resource(tasks.PeepdfByTask, '/tasks/<task_id>/peepdf/')
api.add_resource(tasks.GeolocationByTask, '/tasks/<task_id>/geolocation/')

# Jobs
api.add_resource(jobs.JobList, '/jobs/')
api.add_resource(jobs.Job, '/jobs/<job_id>/')
api.add_resource(jobs.JobsBySchedule, '/schedules/<schedule_id>/jobs/')

# Schedules
api.add_resource(schedules.ScheduleList, '/schedules/')
api.add_resource(schedules.Schedule, '/schedules/<schedule_id>/')

# User agents
api.add_resource(useragents.UserAgentList, '/useragents/')

# DOM events
api.add_resource(domevents.DomEventsList, '/domevents/')

# Plugins versions
api.add_resource(plugins.PluginsList, '/plugins/')

# Authentication
api.add_resource(auth.Login, '/auth/login/')
api.add_resource(auth.Register, '/auth/register/')
api.add_resource(auth.PasswordChange, '/auth/passwordchange/')
