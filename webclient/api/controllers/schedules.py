from bson import json_util
from flask import Response
from flask_restful import Resource, reqparse
from webclient.api.models.schedules import get_schedule, get_schedules, delete_schedule, update_schedule
from webclient.api.utils.decorators import handle_errors


class Schedule(Resource):
    @classmethod
    @handle_errors
    def get(cls, schedule_id):
        schedule = get_schedule(schedule_id)
        response = Response(json_util.dumps({'schedule': schedule}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    def delete(cls, schedule_id):
        delete_schedule(schedule_id)
        response = Response(json_util.dumps({'schedule': None}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    def put(cls, schedule_id):
        parser = reqparse.RequestParser()

        parser.add_argument('enabled', type=bool, help='Schedule state')
        parser.add_argument('name', type=str, help='Schedule name')

        args = parser.parse_args()

        schedule = update_schedule(schedule_id, args)
        response = Response(json_util.dumps({'schedule': schedule}), mimetype='application/json')

        return response


class ScheduleList(Resource):
    @classmethod
    @handle_errors
    def get(cls):
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=str, location='args')

        args = parser.parse_args()

        schedules = get_schedules(args)
        response = Response(schedules, mimetype='application/json')

        return response
