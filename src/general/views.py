import json
import mimetypes
from collections import OrderedDict
from copy import deepcopy

from flask import request, current_app, make_response, stream_with_context
from flask.views import View
from flask_login import UserMixin, current_user
from werkzeug.wrappers import Response

from apps.users.jsonwebtoken import JWTError, JSONWebToken
from apps.users.models import User
from extensions import db, login_manager
from .exceptions import (BadRequestError, NotFoundError, AccessDeniedError,
                         UnauthorizedError, AppValueError)
from .utils import url_for, JSONEncoder


class BaseAPIView(View):
    methods = ['get', 'post', 'put', 'delete']

    __headers = None

    current_app = None
    current_user: User = None
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

        return (json.dumps(response, cls=JSONEncoder), self.status,
                self.__headers)

    def __render_file(self, data):
        if self.file_metadata.get('stream', False):
            ctx = data.iter_content(chunk_size=512)
            resp = Response(stream_with_context(ctx))
        else:
            resp = make_response(data)

        filename = self.file_metadata['filename']
        ext = '.' + filename.split('.')[-1]

        resp.headers['Content-Disposition'] = 'attachment; filename=' + filename
        resp.headers['Content-Type'] = self.file_metadata.get(
            'content_type', mimetypes.types_map.get(ext)
        )

        return resp

    def __generate_response_links(self):
        q_params = self.request.args.copy()

        links = OrderedDict({})
        links['self'] = self.__build_url(q_params)

        if self.limit:
            if self.current_page and self.current_page > 1:
                q_params['page'] = self.current_page - 1
                links['prev'] = self.__build_url(q_params)

            if self.next_page:
                q_params['page'] = self.next_page
                links['next'] = self.__build_url(q_params)

        return links

    def __build_url(self, q_params):
        r = self.request
        base = f'{r.scheme}://{r.host}{r.path}'

        if not q_params:
            return base

        para = '&'.join([f'{k}={v}' for k, v in q_params.items()])
        return f'{base}?{para}'

    def dispatch_request(self, *args, **kwargs):
        self.current_app = current_app
        self.logger = self.current_app.logger
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

        # noinspection PyBroadException

        is_error = False

        try:
            if current_user.is_authenticated:
                self.current_user = current_user.user

            data = method(*args, **kwargs)
            db.session.commit()

        except (BadRequestError, AppValueError) as e:
            self.status = 400
            data = {'error': e.message or 'bad request'}
            is_error = True

        except UnauthorizedError as e:
            self.status = 401
            data = {'error': e.message or 'unauthorized'}
            is_error = True

        except AccessDeniedError as e:
            self.status = 403
            data = {'error': e.message or 'access denied'}
            is_error = True

        except NotFoundError as e:
            self.status = 404
            data = {'error': e.message or 'not found'}
            is_error = True

        except Exception as e:
            error_text = str(e)

            self.logger.error(error_text, exc_info=True)

            if not self.current_app.config['DEBUG']:
                error_text = 'unknown error'

            self.status = 500
            data = {'error': error_text}
            is_error = True

        if not is_error:
            if self.raw_response and isinstance(data, (Response, str)):
                return data
            elif self.file_metadata:
                return self.__render_file(data)
        else:
            db.session.rollback()

        return self.__render(data)

    def add_header(self, header, value):
        if self.__headers is None:
            self.__headers = {}
        self.__headers[header] = value

    def add_location_header(self, url):
        self.add_header('Location', url)

    def available_json_data(self, include=None, exclude=None):
        exclude_columns = {'id_', 'created_date', 'modified_date'}
        exclude_columns -= include or set()
        exclude_columns |= exclude or set()

        return {k: deepcopy(v) for k, v in self.request.json.items()
                if k not in exclude_columns}


class HealthCheckView(BaseAPIView):
    # noinspection PyMethodMayBeStatic
    def get(self):
        return None


class IndexView(BaseAPIView):
    # noinspection PyMethodMayBeStatic
    def get(self):
        return OrderedDict([
            ('sessions', url_for('general.sessions_view'))
        ])


# Flask login stuff

class CurrentUser(UserMixin):
    user: User = None

    def __init__(self, user: User):
        self.user = user

    def get_id(self):
        return self.user.id_


@login_manager.request_loader
def load_user_from_request(req):
    header = req.headers.get('Authorization')
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

    return CurrentUser(user)
