import enum
import inspect
import json
import re
from datetime import datetime
from uuid import UUID

import pytz
from flask import current_app
from flask import url_for as uf

from .exceptions import UnexpectedArguments


# noinspection PyPep8Naming
class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, datetime):
            return isoformat(o)
        if isinstance(o, UUID):
            return str(o)
        super(JSONEncoder, self).default(o)


def url_for(endpoint, **kwargs):
    if '_external' not in kwargs:
        kwargs['_external'] = True

    if not current_app.config['DEBUG'] and '_scheme' not in kwargs:
        kwargs['_scheme'] = 'https'

    url = uf(endpoint, **kwargs)
    url = re.sub(r'/{/', r'{/', url)

    return url


def isoformat(timestamp):
    return timestamp.replace(tzinfo=pytz.UTC).isoformat()


def check_kwargs(func, kwargs):
    spec = inspect.getfullargspec(func)
    unexpected_args = set(kwargs.keys()) - set(spec.args)
    if len(unexpected_args) != 0:
        args = ','.join(unexpected_args)
        plural = '' if len(unexpected_args) == 1 else 's'

        raise UnexpectedArguments(f'{func.__name__}() got an unexpected '
                                  f'keyword argument{plural} {args}')
