from datetime import datetime, timedelta

import jwt
from flask import current_app

from general.exceptions import JWTError
from general.utils import JSONEncoder
from .models import User


class JSONWebToken:
    def __init__(self):
        settings = current_app.config.get('JWTAUTH_SETTINGS', {})
        self.__algorithm = settings.get('ALGORITHM', 'HS256')
        self.__secret_key = current_app.config['SECRET_KEY']

        days = settings.get('EXPIRES', 365)
        self.expires = datetime.utcnow() + timedelta(days=days)

    def __decode_token(self, token):
        return jwt.decode(
            token, self.__secret_key, algorithms=[self.__algorithm]
        )

    def get_token(self, user: User):
        payload = {
            'user_id': user.id_,
            'exp': self.expires
        }

        encoded = jwt.encode(payload, key=self.__secret_key,
                             algorithm=self.__algorithm,
                             json_encoder=JSONEncoder)
        return encoded.decode('utf-8')

    def get_user(self, token):
        try:
            payload = self.__decode_token(token)

        except jwt.ExpiredSignatureError:
            msg = 'Token has expired.'
            raise JWTError(msg)

        except jwt.DecodeError:
            msg = 'Error decoding token.'
            raise JWTError(msg)

        user_id = payload['user_id']
        if not user_id:
            msg = 'Invalid payload.'
            raise JWTError(msg)

        return User.get_auth_user(id_=user_id)
