import importlib
import json
import logging

import time
from flask import Flask, g
from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from werkzeug.exceptions import HTTPException

from mvapi.libs.database import db
from mvapi.libs.error import save_error
from mvapi.libs.exceptions import ModelKeyError, NotFoundError
from mvapi.libs.misc import import_object
from mvapi.settings import settings
from mvapi.web.libs.exceptions import AccessDeniedError, AppException, \
    AppValueError, BadRequestError, NoConverterException, \
    NoExtensionException, NotAllowedError, UnauthorizedError, \
    UnexpectedArgumentsError

logger = logging.getLogger(__name__)


class AppFactory:
    __instance = None
    app = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(AppFactory, cls).__new__(cls)
            cls.__instance.__create_app()

        return cls.__instance

    def __create_app(self):
        self.app = Flask(settings.APP_NAME)
        self.app.config.from_object(settings)

        self.__register_converters()
        self.__bind_extensions()
        self.__register_blueprints()

        if 'EMAILS_MODULE' in self.app.config:
            importlib.import_module(self.app.config['EMAILS_MODULE'])

    def __bind_extensions(self):
        extensions = self.app.config.get('EXTENSIONS', []) + [
            'mvapi.web.libs.extensions.cors',
        ]

        for ext_path in extensions:
            try:
                obj = import_object(ext_path)
            except ImportError:
                raise NoExtensionException(f'No {ext_path} extension found')

            if hasattr(obj, 'init_app') and callable(obj.init_app):
                obj.init_app(self.app)
            elif callable(obj):
                obj(self.app)
            else:
                raise NoExtensionException(
                    f'{ext_path} extension has no init_app.'
                )

            ext_name = ext_path.split('.')[-1]
            if ext_name not in self.app.extensions:
                self.app.extensions[ext_name] = obj

    def __register_blueprints(self):
        blueprints = self.app.config.get('BLUEPRINTS', []) + [
            'mvapi.web.urls.general_bp',
            'mvapi.web.urls.api_bp',
        ]

        for blueprint_path in blueprints:
            try:
                obj = import_object(blueprint_path)
                self.app.register_blueprint(obj)

            except ImportError:
                raise NoExtensionException(
                    f'No {blueprint_path} blueprint found'
                )

    def __register_converters(self):
        for name, path in self.app.config.get('CONVERTERS', ()):
            try:
                converter = import_object(path)
                self.app.url_map.converters[name] = converter

            except ImportError:
                raise NoConverterException(f'No {name} converter found')


def create_app():
    app = AppFactory().app

    if settings.DEBUG:
        @app.before_request
        def before_request():
            g.start = time.time()

        @app.after_request
        def after_request(response):
            diff = time.time() - g.start
            logger.debug(f'Request finished in {diff}')

            return response

    @app.teardown_appcontext
    def teardown_appcontext(exception):
        if exception:
            db.session.rollback()
        else:
            db.session.commit()

        db.session.remove()

    def app_error_response(error, status, default_text):
        db.session.rollback()

        errors_text = '; '.join(error.args) if error.args else default_text

        if not settings.DEBUG and not (
                isinstance(error, AppException) and
                not isinstance(error, UnexpectedArgumentsError)):
            errors_text = default_text

        if status == 500:
            logger.error(errors_text, exc_info=True)

        data = {
            'errors': errors_text.split('; '),
            'status': str(status)
        }

        # TODO: Change it to use the common response class

        return json.dumps(data), status, {
            'Content-Type': 'application/json; charset=utf-8'
        }

    @app.errorhandler(Exception)
    def error_handler(error):
        if isinstance(error, (BadRequestError, AppValueError, ModelKeyError,)):
            return app_error_response(error, 400, 'Bad request')

        if isinstance(error, UnauthorizedError):
            return app_error_response(error, 401, 'Unauthorized')

        if isinstance(error, AccessDeniedError):
            return app_error_response(error, 403, 'Access denied')

        if isinstance(error, (NotFoundError, UnexpectedArgumentsError,)):
            return app_error_response(error, 404, 'Not found')

        if isinstance(error, NotAllowedError):
            return app_error_response(error, 405, 'Method not allowed')

        if isinstance(error, HTTPException):
            return app_error_response(error, error.code, error.name)

        save_error()

        return app_error_response(error, 500, 'Unknown error')

    if settings.DEBUG_SQL:
        # noinspection PyUnusedLocal
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context,
                                  executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            logger.debug(f'Start Query: {statement}. '
                         f'With parameters: {parameters}')

        # noinspection PyUnusedLocal
        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context,
                                 executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            logger.debug(f'Query Complete. Total Time: {str(total)}\n')

    return app
