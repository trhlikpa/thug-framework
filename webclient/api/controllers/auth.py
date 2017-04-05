from bson import json_util
from flask_restful import Resource, reqparse
from flask import Response, abort, g
from webclient.api.models.users import validate_user, create_user, change_password
from webclient.api.utils.decorators import handle_errors, login_required


class PasswordChange(Resource):
    @classmethod
    @handle_errors
    @login_required
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str, help='Old login password', required=True)
        parser.add_argument('new_password', type=str, help='New login password', required=True)
        parser.add_argument('new_password_confirm', type=str, help='New login password confirmation', required=True)

        args = parser.parse_args()

        if not g.user or not g.user['email']:
            abort(401, message='Invalid user ID')

        password = args.get('password')
        new_password = args.get('new_password')
        new_password_confirm = args.get('new_password_confirm')

        result = change_password(g.user['email'], password, new_password, new_password_confirm)
        response = Response(json_util.dumps({'result': result}), mimetype='application/json')

        return response


class Login(Resource):
    """
    Resource representing '/api/v1.0/auth/login/' api route

    available methods: POST
    """

    @classmethod
    @handle_errors
    def post(cls):
        """
        Logins user

        POST /api/v1.0/auth/login/

        Request body parameters:
            :email: login email
            :password: login password

        :return: JSON web token
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Login email address', required=True)
        parser.add_argument('password', type=str, help='Login password', required=True)

        args = parser.parse_args()

        email = args.get('email')
        password = args.get('password')

        token = validate_user(email, password)
        return {'token': token}


class Register(Resource):
    """
    Resource representing '/api/v1.0/auth/register/' api route

    available methods: POST
    """

    @classmethod
    @handle_errors
    def post(cls):
        """
        Creates user

        POST /api/v1.0/auth/register/

        Request body parameters:
            :name: user name
            :email: user email address
            :password: user password
            :password_confirm: password confirmation

        :return: Newly created user ID
        """
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, help='User name', required=True)
        parser.add_argument('email', type=str, help='User email address', required=True)
        parser.add_argument('password', type=str, help='User password', required=True)
        parser.add_argument('password_confirm', type=str, help='Password confirmation', required=True)

        args = parser.parse_args()

        email = args.get('email')
        password = args.get('password')
        password_confirm = args.get('password_confirm')
        name = args.get('name')

        user_id = create_user(name, email, password, password_confirm)
        response = Response(json_util.dumps({'user': user_id}), mimetype='application/json')

        return response
