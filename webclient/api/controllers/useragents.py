from flask_restful import Resource
from flask import Response
from webclient.api.models.useragents import get_useragents


class UserAgentList(Resource):
    @classmethod
    def get(cls):
        agents = get_useragents()
        response = Response(agents, mimetype='application/json')
        return response
