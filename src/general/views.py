from collections import OrderedDict
import json

from flask import request, current_app, make_response
from flask.views import View

from .exceptions import (BadRequestError, NotFoundError, AccessDeniedError,
                         UnauthorizedError)
from .utils import url_for
from apps.users.jsonwebtoken import JWTError, JSONWebToken


class BaseAPIView(View):
    methods = ['get', 'post', 'put', 'delete']

    __headers = None

    current_app = None
    current_user = None
    logger = None
    request = None
    raw_response = False
    file_metadata = None

    status = 200
    limit = 30
    next_page = None
    current_page = None

    @property
    def offset(self):
        return self.limit * (self.current_page - 1) if self.limit else 0

    def __render(self, data):
        self.add_header('Content-Type', 'application/json; charset=utf-8')

        if self.status not in [200, 201]:
            response = data
        else:
            data_exists = False
            if data is not None:
                data_exists = True
                if not isinstance(data, list):
                    data = [data]

                if (self.limit and not self.next_page and
                        len(data) == self.limit):
                    self.next_page = self.current_page + 1

            response = OrderedDict({})
            response['links'] = self.__generate_response_links()

            if data_exists:
                response['items'] = data

        return json.dumps(response), self.status, self.__headers

    def __render_file(self, data):
        resp = make_response(data)

        filename = self.file_metadata['filename']
        resp.headers['Content-Disposition'] = 'attachment; filename=' + filename
        resp.headers['Content-Type'] = self.file_metadata['content_type']

        return resp

    def __generate_response_links(self):
        q_params = self.request.args.copy()

        links = OrderedDict({})
        links['self'] = self.__build_url(q_params)

        if self.limit and self.next_page:
            q_params['page'] = self.next_page
            links['next'] = self.__build_url(q_params)

        return links

    def __build_url(self, q_params):
        base = '{}://{}{}'.format(
            self.request.headers.get('X-Forwarded-Proto', 'http'),
            self.request.host,
            self.request.path
        )

        if not q_params:
            return base

        return '{}?{}'.format(
            base,
            '&'.join(['{}={}'.format(k, v) for k, v in q_params.items()])
        )

    def __get_current_user(self):
        header = self.request.headers.get('Authorization')
        if not header:
            return None

        try:
            token_type, access_token = header.split(' ')
        except ValueError:
            raise BadRequestError('Wrong authorization header')

        if token_type.lower() != 'bearer':
            raise BadRequestError('Wrong authorization token type')

        jwt = JSONWebToken()

        try:
            user = jwt.get_user(access_token)
        except (NotFoundError, JWTError):
            return None

        return user

    def dispatch_request(self, *args, **kwargs):
        self.current_app = current_app
        self.logger = current_app.logger
        self.request = request
        self.raw_response = False

        method = getattr(self, self.request.method.lower(), None)
        if method is None and self.request.method.lower() == 'head':
            method = getattr(self, 'get', None)

        if not method:
            self.status = 405
            return self.__render({'error': 'method not allowed'})

        if self.request.method.lower() in ['get', 'head']:
            self.limit = int(self.request.args.get('limit', self.limit))
            self.current_page = int(self.request.args.get('page', 1))

        if self.request.method.lower() == 'post':
            self.status = 201

        try:
            self.current_user = self.__get_current_user()
            data = method(*args, **kwargs)

        except BadRequestError as e:
            self.status = 400
            data = {'error': e.message or 'bad request'}

        except UnauthorizedError as e:
            self.status = 401
            data = {'error': e.message or 'unauthorized'}

        except AccessDeniedError as e:
            self.status = 403
            data = {'error': e.message or 'access denied'}

        except NotFoundError as e:
            self.status = 404
            data = {'error': e.message or 'not found'}

        if self.raw_response:
            return data
        elif self.file_metadata:
            return self.__render_file(data)

        return self.__render(data)

    def add_header(self, header, value):
        if self.__headers is None:
            self.__headers = {}
        self.__headers[header] = value


class IndexView(BaseAPIView):
    # noinspection PyMethodMayBeStatic
    def get(self):
        return OrderedDict([
            ('sessions', url_for('general.sessions_view'))
        ])
