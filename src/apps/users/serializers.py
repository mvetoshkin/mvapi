from collections import OrderedDict

from .models import User
from general.utils import url_for


def user_serializer(obj: User):
    return OrderedDict([
        ('id', obj.id_),
        ('url', url_for('users.users_view', user_id=obj.id_)),
        ('email', obj.email),
        ('first_name', obj.first_name),
        ('last_name', obj.last_name),
        ('is_admin', obj.is_admin)
    ])
