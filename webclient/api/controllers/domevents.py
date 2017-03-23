from flask_restful import Resource
from flask import Response
from webclient.api.models.domevents import get_dom_events
from webclient.api.utils.decorators import handle_errors


class DomEventsList(Resource):
    """
    Resource representing '/domevents/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    def get(cls):
        """
        Returns list with supported DOM events

        GET '/domevents/'

        :return: list of DOM events
        """
        events = get_dom_events()
        response = Response(events, mimetype='application/json')
        return response
