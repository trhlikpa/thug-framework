from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.users import validate_user, create_user


class Login(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Email address', required=True)
        parser.add_argument('password', type=str, help='Password', required=True)

        args = parser.parse_args()

        email = args.get('email')
        password = args.get('password')

        try:
            token = validate_user(email, password)
            return {'token': token}
        except Exception as error:
            abort(400, message='Error while loging in: %s' % str(error))


class Register(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='Account name', required=True)
        parser.add_argument('email', type=str, help='Account email address', required=True)
        parser.add_argument('password', type=str, help='Password', required=True)
        parser.add_argument('password_confirm', type=str, help='Password confirmation', required=True)

        args = parser.parse_args()

        email = args.get('email')
        password = args.get('password')
        password_confirm = args.get('password_confirm')
        name = args.get('name')

        user_id = None
        try:
            user_id = create_user(name, email, password, password_confirm)
        except Exception as error:
            abort(400, message='Error while creating account: %s' % str(error))

        response = Response(json_util.dumps({'user': user_id}), mimetype='application/json')
        return response
