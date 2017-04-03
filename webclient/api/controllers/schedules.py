from bson import json_util
from flask import Response
from flask_restful import Resource, reqparse
from webclient.api.models.schedules import get_schedule, get_schedules, delete_schedule, update_schedule
from webclient.api.utils.decorators import handle_errors


class Schedule(Resource):
    """
    Resource representing '/api/v1.0/schedules/<schedule_id>/' api route

    available methods: GET, DELETE, PUT
    """
    @classmethod
    @handle_errors
    def get(cls, schedule_id):
        """
        Returns Schedule with specified schedule_id

        GET /api/v1.0/schedules/<schedule_id>/

        URL parameters:
            :schedule_id: schedule ID

        :return: JSON encoded schedule document; null if not found
        """
        schedule = get_schedule(schedule_id)
        response = Response(json_util.dumps({'schedule': schedule}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    def delete(cls, schedule_id):
        """
        Deletes Schedule with specified schedule_id

        DELETE /api/v1.0/schedules/<schedule_id>/

        URL parameters:
            :schedule_id: schedule ID

        :return: True if removed, False otherwise
        """
        result = delete_schedule(schedule_id)
        response = Response(json_util.dumps({'schedule': result}), mimetype='application/json')

        return response

    @classmethod
    @handle_errors
    def put(cls, schedule_id):
        """
        Updates Schedule with specified schedule_id

        PUT /api/v1.0/schedules/<schedule_id>/

        URL parameters:
            :schedule_id: schedules ID

        Request body parameters:
            :enabled: Pause or resume schedule
            :name: New name

        :return: Schedule ID
        """
        parser = reqparse.RequestParser()

        parser.add_argument('enabled', type=bool, help='Schedule state')
        parser.add_argument('name', type=str, help='Schedule name')

        args = parser.parse_args()

        schedule = update_schedule(schedule_id, args)
        response = Response(json_util.dumps({'schedule': schedule}), mimetype='application/json')

        return response


class ScheduleList(Resource):
    """
    Resource representing '/api/v1.0/schedules/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    def get(cls):
        """
        Returns list of schedules

        GET /api/v1.0/schedules/

        Query string arguments:

        :sort: field and direction to sort on, default: '_id|1'
        :page: page to show
        :per_page: entries per page
        :filter: phrase to filter

        :return: list of schedules
        """
        parser = reqparse.RequestParser()

        parser.add_argument('sort', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        parser.add_argument('filter', type=unicode, location='args')

        args = parser.parse_args()

        schedules = get_schedules(args)
        response = Response(schedules, mimetype='application/json')

        return response
