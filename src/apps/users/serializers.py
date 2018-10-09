from collections import OrderedDict

from general.utils import url_for
from .jsonwebtoken import JSONWebToken
from .models import User


def user_serializer(obj: User, current_user: User=None):
    resp = OrderedDict([
        ('id', obj.id_),
        ('url', url_for('users.users_view', user_id=obj.id_)),
        ('created_date', obj.created_date),
        ('first_name', obj.first_name),
        ('last_name', obj.last_name),
    ])

    if current_user and (obj.id_ == current_user.id_ or current_user.is_admin):
        resp['email'] = obj.email
        if current_user.is_admin:
            resp['is_admin'] = obj.is_admin

    return resp


def access_token_serializer(obj: User):
    jwt = JSONWebToken()
    token = jwt.get_token(user=obj)

    return OrderedDict([
        ('access_token', token),
        ('token_type', 'Bearer'),
        ('expires', jwt.expires)
    ])
