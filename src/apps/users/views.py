from collections import OrderedDict

from general.decorators import owner_required
from general.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from general.views import BaseAPIView
from .models import User
from .serializers import user_serializer, access_token_serializer


class UsersView(BaseAPIView):
    @owner_required()
    def get(self, user_id=None):
        if not user_id and not self.current_user.is_admin:
            raise NotFoundError

        if user_id:
            users = [User.get(id_=user_id)]
        else:
            users = User.all(**self.common_args)

        return [user_serializer(user, current_user=self.current_user)
                for user in users]

    def post(self):
        try:
            kwargs = {
                'email': self.json_data['email'],
                'password': self.json_data['password']
            }

        except KeyError:
            raise BadRequestError

        try:
            user = User.find_by_email(email=kwargs['email'])
            if not user.passwords_matched(password=kwargs['password']):
                raise UnauthorizedError
            self.status = 200
        except NotFoundError:
            user = User.create(**kwargs)

        user_resp = user_serializer(user, current_user=user)
        if self.status == 201:
            self.add_location_header(user_resp['url'])

        return OrderedDict([
            ('user', user_resp),
            ('access_token', access_token_serializer(user))
        ])

    @owner_required()
    def put(self, user_id):
        user = User.get(id_=user_id)

        excluded_fields = {'email'}

        if not self.current_user.is_admin:
            excluded_fields.add('is_admin')

        data = self.available_json_data(exclude=excluded_fields)
        user.populate(**data)

        return user_serializer(user, current_user=self.current_user)

    @owner_required()
    def delete(self, user_id):
        user = User.get(id_=user_id)
        user.delete()


class SessionsView(BaseAPIView):
    def post(self):
        try:
            email = self.json_data['email']
            password = self.json_data['password']
        except KeyError:
            raise BadRequestError

        try:
            user = User.find_by_email(email=email, check_all=True)
        except NotFoundError:
            raise UnauthorizedError

        if not user.passwords_matched(password=password):
            raise UnauthorizedError

        return OrderedDict([
            ('user', user_serializer(user, current_user=user)),
            ('access_token', access_token_serializer(user))
        ])
