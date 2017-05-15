from flask_restful import Resource
from flask import Response
from webapp.api.models.useragents import get_useragents
from webapp.api.utils.decorators import handle_errors


class UserAgentList(Resource):
    """
    Resource representing '/useragents/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    def get(cls):
        """
        Returns thug useragents

        GET '/useragents/'

        :return: list of thug user agents
        """
        agents = get_useragents()
        response = Response(agents, mimetype='application/json')
        return response
