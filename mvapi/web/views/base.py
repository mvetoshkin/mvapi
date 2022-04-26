import re
from copy import deepcopy

from flask import g, request
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest

from mvapi.libs.exceptions import NotFoundError
from mvapi.settings import settings
from mvapi.web.libs.exceptions import AccessDeniedError, BadRequestError, \
    UnauthorizedError
from mvapi.web.libs.misc import ApiResponse
from mvapi.web.models.user import User


class BaseView:
    resource_type = None
    resource_model = None

    current_user: User = None
    resource_id = None
    relationship_type = None
    related_relationship_type = None
    resource = None
    request_attrs = None
    request_relationships = None
    limit = 0
    current_page = 1
    next_page = None
    cursor = None
    common_args = None
    return_fields = None

    def __init__(self, **kwargs):
        self.current_user = g.current_user

        self.resource_id = kwargs.get('resource_id')
        self.relationship_type = kwargs.get('relationship_type')
        self.related_relationship_type = kwargs.get('related_relationship_type')

        self.limit = settings.LIMIT

    def __get_offset(self):
        return self.limit * (self.current_page - 1) if self.limit else 0

    def __process_request_args(self):
        self.common_args = {
            'limit': self.limit,
            'offset': self.__get_offset()
        }

        for key, value in request.args.items():
            key = key.lower()

            if key in ('include',):
                continue

            match = re.match(r'page\[([a-zA-Z0-9]+)]', key)
            if match:
                self.process_page_arg(page=match.group(1), value=value)
                continue

            match = re.match(r'filter\[([a-zA-Z0-9_]+)]', key)
            if match:
                self.process_filter_arg(filter_=match.group(1), value=value)
                continue

            match = re.match(r'fields\[([a-zA-Z0-9_]+)]', key)
            if match:
                self.process_fields_arg(field=match.group(1), value=value)
                continue

            method = getattr(self, f'process_{key}_arg', None)
            if method:
                method(value)
                continue

            raise BadRequestError

    def __process_json_data(self):
        self.request_attrs = {}
        self.request_relationships = {}

        try:
            json_data = request.json or {}
            json_data = json_data.get('data', {})
        except BadRequest:
            return

        if self.relationship_type:
            self.__process_relationship(relationship=self.relationship_type,
                                        data=json_data)

        else:
            for key, value in json_data.get('attributes', {}).items():
                func = getattr(self, f'get_{key}_attribute', None)
                self.request_attrs[key] = func(value) if func else value

            for key, value in json_data.get('relationships', {}).items():
                self.__process_relationship(relationship=key,
                                            data=value['data'])

        if self.resource_model:
            self.__check_nullables()

    def __process_relationship(self, relationship, data):
        if self.resource_model:
            rel_attr = getattr(self.resource_model, relationship, None)
            if (not rel_attr or
                    (type(data) is list) != rel_attr.property.uselist):
                raise BadRequestError

        func = getattr(self, f'get_{relationship}_relationship', None)
        if not func:
            raise NotImplementedError

        if not data:
            results = data

        elif type(data) is list:
            try:
                results = func([item['id'] for item in data])
            except NotFoundError:
                raise BadRequestError

            if len(results) != len(data):
                raise BadRequestError

            if type(results) is not list:
                results = [results]

        else:
            try:
                results = func(data['id'])
            except NotFoundError:
                raise BadRequestError

            if not results:
                raise BadRequestError

            if type(results) is list:
                results = results[0]

        self.request_relationships[relationship] = results

    def __check_nullables(self):
        for key in (self.resource_model.required_keys &
                    set(self.request_attrs.keys())):
            value = self.request_attrs[key]

            if type(value) is bool and value is False:
                continue

            if not value:
                raise BadRequestError(
                    f'Attribute {key} can\'t be null or empty'
                )

        for key in (self.resource_model.required_keys &
                    set(self.request_relationships.keys())):
            if not self.request_relationships[key]:
                raise BadRequestError(
                    f'Relationship {key} can\'t be null or empty'
                )

    def process_request(self):
        req_method = request.method.lower()
        self.__process_request_args()

        if (req_method == 'post' and self.resource_id and
                not self.relationship_type and
                not self.related_relationship_type):
            raise NotFoundError

        if self.related_relationship_type:
            if req_method not in ('head', 'get'):
                raise NotFoundError

            self.resource = self.get_resource()
            if not self.resource:
                raise NotFoundError

            f_name = f'process_{self.related_relationship_type}_relationship'
            func = getattr(self, f_name, None)
            if func:
                return func()

            attr = getattr(self.resource, self.related_relationship_type, None)
            if attr:
                if isinstance(attr, Query):
                    return attr.apply_args(**self.common_args)
                else:
                    return attr
            else:
                raise NotFoundError

        method_name = req_method
        if self.relationship_type:
            if req_method not in ('post', 'patch', 'delete'):
                raise NotFoundError

            method_name = f'{req_method}_{self.relationship_type}_relationship'

        method = getattr(self, method_name, None)
        if method is None and req_method == 'head':
            method = getattr(self, 'get', None)

        if not method:
            raise NotFoundError

        if (req_method in ('post', 'patch', 'delete',) and
                not request.files):
            self.__process_json_data()

        # Disallow updating a whole relationship collection for a resource
        # when patching the resource itself
        if not self.relationship_type and req_method in ('patch',):
            for value in self.request_relationships.values():
                if type(value) is list:
                    raise BadRequestError

        if self.resource_id:
            self.resource = self.get_resource()

        data = method()

        meta = None
        if type(data) is tuple:
            data, meta = data

        if data is None:
            data = self.resource

        if isinstance(data, Query):
            data = data.all()

        return ApiResponse(
            data=data,
            meta=meta,
            limit=self.limit,
            current_page=self.current_page,
            next_page=self.next_page,
            cursor=self.cursor,
            relationship_type=self.relationship_type,
            related_relationship_type=self.related_relationship_type,
            return_fields=self.return_fields
        )

    def available_data(self, include=None, exclude=None, required=None,
                       extra=None):
        exclude_columns = {'id', 'created_date', 'modified_date'}
        exclude_columns -= include or set()
        exclude_columns |= exclude or set()

        attr_keys, rel_keys = set(), set()
        if self.resource_model:
            attr_keys = self.resource_model.available_columns
            rel_keys = self.resource_model.relationship_keys

        attr_keys |= include or set()
        attr_keys |= required or set()
        attr_keys |= extra or set()

        data = {
            k: deepcopy(v) for k, v in self.request_attrs.items()
            if not attr_keys or (k in attr_keys and k not in exclude_columns)
        }

        data.update({
            k: deepcopy(v)
            for k, v in self.request_relationships.items()
            if not rel_keys or (k in rel_keys and type(v) is not list)
        })

        if required:
            errors = []
            for key in required:
                val = data.get(key)
                if not val and key in self.resource_model.available_columns:
                    column_name = self.resource_model.readable_column_name(key)
                    errors.append(f'{column_name} is required')

            if errors:
                raise BadRequestError('; '.join(errors))

        for attr, value in data.items():
            func = getattr(self, f'check_{attr}_value', None)
            if func:
                func(value)

        return data

    def drop_relationships(self, name, existing=False, missing=False,
                           resource=None):
        resource = resource or self.resource
        rel_items = self.request_relationships[name]
        relationship = getattr(resource, name)
        relationship_cls = relationship.attr.target_mapper.class_

        items = relationship.apply_args(limit=0, filters=[
            relationship_cls.id_.in_({i.id_ for i in rel_items})
        ])

        item_ids = {i.id_ for i in items}

        if existing:
            return filter(lambda i: i.id_ not in item_ids, rel_items)
        if missing:
            return filter(lambda i: i.id_ in item_ids, rel_items)

        return rel_items

    def check_owner(self, resource_user: User):
        if not self.current_user:
            raise UnauthorizedError

        if self.current_user.id_ != resource_user.id_ and \
                not self.current_user.is_admin:
            raise AccessDeniedError

    def get_resource_owner(self, param_name=None):
        return self.resource if not param_name else \
            getattr(self.resource, param_name)

    def get_resource(self):
        if self.resource:
            return self.resource

        if self.resource_model and self.resource_id:
            return self.resource_model.query.get(self.resource_id)

        raise NotFoundError

    def get_resources(self, allow_all=False):
        if allow_all or (self.current_user and self.current_user.is_admin):
            return (
                self.get_resource() if self.resource_id
                else self.resource_model.query.apply_args(**self.common_args)
            )

        else:
            if self.resource_id:
                return self.get_resource()

            raise AccessDeniedError

    def process_sort_arg(self, value):
        self.common_args['sort'] = self.resource_model.get_sort_fields(value)

    def process_page_arg(self, page, value):
        page = page.lower()

        if page == 'size':
            self.limit = int(value)
            self.common_args['limit'] = self.limit

        if page == 'number':
            self.current_page = int(value)

        self.common_args['offset'] = self.__get_offset()

    def process_filter_arg(self, filter_, value):
        filter_ = filter_.lower()
        method = getattr(self, f'get_{filter_}_filter', None)
        if not method:
            raise BadRequestError(f'Filter {filter_} is not supported')

        filters = method(value)
        if filters:
            if 'filters' not in self.common_args:
                self.common_args['filters'] = []

            self.common_args['filters'] += filters

    def process_fields_arg(self, field, value):
        if self.return_fields is None:
            self.return_fields = {}

        self.return_fields[field] = value.split(',')

    def get_ids_filter(self, ids):
        if not ids:
            return []

        ids = ids.replace(', ', ',').lower().split(',')
        return [self.resource_model.id_.in_(ids)]
