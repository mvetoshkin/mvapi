from datetime import datetime, timedelta

import jwt

from mvapi.settings import settings
from mvapi.web.libs.exceptions import JWTError
from mvapi.web.libs.misc import JSONEncoder
from mvapi.web.models.session import Session


class JSONWebToken:
    token_type = 'Bearer'
    expires = None

    __algorithm = None
    __secret_key = None
    __expires_from = None

    def __init__(self, expires_from=None, temp=False):
        jwt_settings = settings.JWTAUTH_SETTINGS

        self.__algorithm = jwt_settings.get('ALGORITHM', 'HS256')
        self.__secret_key = settings.SECRET_KEY
        self.__expires_from = expires_from or datetime.utcnow()

        if temp:
            self.expires = self.__get_expires(hours=1)
        else:
            days = jwt_settings.get('EXPIRES', 365)
            self.expires = self.__get_expires(days=days)

    def __decode_token(self, token):
        return jwt.decode(
            token, self.__secret_key, algorithms=[self.__algorithm]
        )

    def __get_expires(self, days=0, hours=0):
        return self.__expires_from + timedelta(days=days, hours=hours)

    def get_token(self, session: Session):
        payload = {
            'session_id': session.id_,
            'exp': self.expires
        }

        return jwt.encode(payload, key=self.__secret_key,
                          algorithm=self.__algorithm,
                          json_encoder=JSONEncoder)

    def get_user(self, token):
        try:
            payload = self.__decode_token(token)

        except jwt.ExpiredSignatureError:
            raise JWTError('Token has expired')

        except jwt.DecodeError:
            raise JWTError('Error decoding token')

        session_id = payload.get('session_id')
        if not session_id:
            raise JWTError('Invalid payload')

        session = Session.query.get(session_id)
        return session.user
