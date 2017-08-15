from datetime import datetime, timedelta

from flask import current_app
import jwt

from .models import User
from general.exceptions import JWTError


class JSONWebToken:
    def __init__(self):
        settings = current_app.config.get('JWTAUTH_SETTINGS', {})
        self.__algorithm = settings.get('ALGORITHM', 'HS256')
        self.__secret_key = current_app.config.get('SECRET_KEY')

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

        encoded = jwt.encode(payload, self.__secret_key, self.__algorithm)
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

        return User.get(id_=user_id)
