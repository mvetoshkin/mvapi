from collections import OrderedDict

from .jsonwebtoken import JSONWebToken
from .models import User
from .serializers import user_serializer
from general.decorators import auth_required, owner_required
from general.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from general.views import BaseAPIView


class UsersView(BaseAPIView):
    @auth_required
    @owner_required
    def get(self, user_id):
        user = User.get(id_=user_id)
        return user_serializer(user)


class SessionsView(BaseAPIView):
    def post(self):
        try:
            email = self.request.json['email']
            password = self.request.json.get('password')
        except KeyError:
            raise BadRequestError

        try:
            user = User.find_by_email(email=email)
        except NotFoundError:
            raise UnauthorizedError

        if not user.passwords_matched(password=password):
            raise UnauthorizedError

        self.status = 200

        jwt = JSONWebToken()
        token = jwt.get_token(user=user)

        return OrderedDict([
            ('user', user_serializer(user)),
            ('access_token', OrderedDict([
                ('access_token', token),
                ('token_type', 'Bearer'),
                ('expires', jwt.expires.isoformat())
            ]))
        ])
