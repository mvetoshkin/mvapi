import enum
import json
from datetime import date, datetime, timezone
from uuid import UUID

from flask import request, url_for as uf


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, datetime):
            return isoformat_with_timezone(o)
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        super(JSONEncoder, self).default(o)


def isoformat_with_timezone(timestamp):
    return timestamp.replace(tzinfo=timezone.utc).isoformat()


def is_local_dev_host():
    return '0.0.0.0' in request.host or \
           'localhost' in request.host or \
           '127.0.0.1' in request.host


def dict_value(dict_: dict, path: str, default=None):
    chunks = path.split('.')

    for idx, chunk in enumerate(chunks):
        if not isinstance(dict_, dict):
            raise KeyError

        if idx == len(chunks) - 1:
            return dict_.get(chunk, default)
        else:
            dict_ = dict_.get(chunk, {})


def url_for(endpoint, **kwargs):
    local_dev = is_local_dev_host()
    def_scheme = 'http' if local_dev else 'https'
    scheme = kwargs.get('_scheme', def_scheme)

    # Flask's url_for is pretty slow, and as long as JSON API has a certain urls
    # format we can build urls just concatenating pieces
    if endpoint == 'api.api_view':
        resource_type = kwargs.get('resource_type')
        resource_id = kwargs.get('resource_id')
        relationship_type = kwargs.get('relationship_type')
        related_relationship_type = kwargs.get('related_relationship_type')

        chunks = [request.host, 'api', resource_type, str(resource_id)]

        if relationship_type:
            chunks.append('relationships')
            chunks.append(relationship_type)

        elif related_relationship_type:
            chunks.append(related_relationship_type)

        return scheme + '://' + '/'.join(chunks)

    if '_external' not in kwargs:
        kwargs['_external'] = True

    kwargs['_scheme'] = scheme
    return uf(endpoint, **kwargs)


class ApiResponse:
    __next_page = None

    data = None
    meta = None
    status = None
    limit = 0
    current_page = 1
    cursor = None
    relationship_type = None
    related_relationship_type = None
    return_fields = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError

    @property
    def next_page(self):
        if type(self.data) is list:
            if self.limit and \
                    not self.__next_page and \
                    len(self.data) == self.limit:
                return self.current_page + 1

        return self.__next_page

    @next_page.setter
    def next_page(self, value):
        self.__next_page = value
