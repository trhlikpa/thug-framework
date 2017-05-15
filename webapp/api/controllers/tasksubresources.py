from bson import json_util
from flask import Response
from flask_restful import Resource
from webapp.api.models.tasksubresources import get_task_subresource
from webapp.api.utils.decorators import handle_errors, login_required


def get_subresource(resource_name):
    """
    Returns subresource

    :param resource_name: name of a subresource
    """
    resource = get_task_subresource(resource_name)
    response = Response(json_util.dumps({resource_name: resource}), mimetype='application/json')

    return response


class Urls(Resource):
    """
    Resource representing '/urls/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns options

        GET /urls/
        """
        return get_subresource('urls')


class Connections(Resource):
    """
    Resource representing '/connections/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns connections

        GET /connections/
        """
        return get_subresource('connections')


class Locations(Resource):
    """
    Resource representing '/locations/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns locations

        GET /locations/
        """
        return get_subresource('locations')


class Samples(Resource):
    """
    Resource representing '/samples/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns samples

        GET /samples/
        """
        return get_subresource('samples')


class Exploits(Resource):
    """
    Resource representing '/exploits/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns exploits

        GET /exploits/
        """
        return get_subresource('exploits')


class Behaviors(Resource):
    """
    Resource representing '/behaviors/' api route

    available methods: GET
    """
    @classmethod
    @handle_errors
    @login_required
    def get(cls):
        """
        Returns behaviors

        GET /behaviors/
        """
        return get_subresource('behaviors')
