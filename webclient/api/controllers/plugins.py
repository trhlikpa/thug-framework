from flask_restful import Resource
from flask import Response
from webclient.api.models.plugins import get_thug_plugins_versions
from webclient.api.utils.decorators import handle_errors


class PluginsList(Resource):
    """
    Resource representing '/plugins/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    def get(cls):
        """
        Returns list with supported plugins versions

        GET '/plugins/'

        :return: plugins versions
        """
        plugins = get_thug_plugins_versions()
        response = Response(plugins, mimetype='application/json')
        return response
