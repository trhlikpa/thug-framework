import bcrypt
import hmac
import datetime
import jwt
from bson import ObjectId
from flask import current_app
from webclient.dbcontext import db
from jwt.exceptions import InvalidTokenError
from validate_email import validate_email


def validate_user(email, password):
    user = db.users.find_one({'email': email})

    if user is None:
        raise LookupError('User account not found')

    hashed = user['password'].encode('utf-8')
    if hmac.compare_digest(bcrypt.hashpw(password.encode('utf-8'), hashed), hashed):
        try:
            token = jwt.encode({'_id': str(user['_id'])}, current_app.config['SECRET_KEY'],
                               algorithm='HS256')
            return token
        except Exception:
            raise InvalidTokenError("Error creating JWToken")
    else:
        raise AssertionError("Incorrect password")


def create_user(name, email, password, password_confirm):
    if not validate_email(email):
        raise AssertionError('Email address is not valid')

    if len(password) < 8:
        raise AssertionError('Password must be at least 8 characters')

    if not any(char.isdigit() for char in password):
        raise AssertionError('Password must contain at least one digit')

    if not any(char.isalpha() for char in password):
        raise AssertionError('Password must contain at least one letter')

    if password != password_confirm:
        raise AssertionError('Password and password confirmation are not the same')

    user = db.users.find_one({'email': email})

    if user is not None:
        raise AssertionError('User with specified email already exists')

    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    input_data = {
        'name': name,
        'email': email,
        'password': hashed,
        'created_time': datetime.datetime.utcnow().isoformat(),
    }

    oid = db.users.insert(input_data)
    return str(oid)


def get_user(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})

    return user
