import jwt
from jwt.exceptions import InvalidTokenError
from functools import wraps
from flask import current_app, request, g
from flask_restful import abort
from webclient.api.models.users import get_user


def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            if 'authorization' not in request.headers:
                abort(404, message='You need log in to access protected resource')

            token = request.headers.get('authorization')
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithm='HS256')
            user_id = decoded_token['_id']
            g.user = get_user(user_id)

            if g.user is None:
                abort(404, message='Invalid user id')

            return func(*args, **kwargs)

        except InvalidTokenError as error:
            abort(400, message='Error while decoding token: %s' % str(error))

    return decorator


def validate_user(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id != g.user['_id']:
            abort(404, message='You need permision to access this resource')

        return func(*args, **kwargs)

    return decorator
