from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.schedules import get_schedule, get_schedules, create_schedule


class Schedule(Resource):
    def get(self, schedule_id):
        schedule = None
        try:
            schedule = get_schedule(schedule_id)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

        response = Response(json_util.dumps({'schedule': schedule}), mimetype='application/json')
        return response


class ScheduleList(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('task', type=str, help='Taskname', required=True)
        parser.add_argument('crontab', type=dict, help='Crontab', required=True)
        parser.add_argument('args', type=dict, action='append', help='args')
        parser.add_argument('kwargs', help='kwargs')

        args = parser.parse_args()

        schedule_id = None
        try:
            schedule_id = create_schedule(args)
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

        response = Response(json_util.dumps({'schedule': schedule_id}), mimetype='application/json')
        return response

    def get(self):
        schedules = None
        try:
            schedules = get_schedules()
        except Exception as error:
            abort(500, message='Error while processing request: %s' % error.message)

        response = Response(json_util.dumps({'schedules': schedules}, default=json_util.default),
                            mimetype='application/json')
        return response
