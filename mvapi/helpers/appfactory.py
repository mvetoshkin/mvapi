import importlib
import json
import logging
import os
import time

from dotenv import load_dotenv
from flask import Flask, g
from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from werkzeug.exceptions import HTTPException

from common.exceptions import AppException, BadRequestError, AppValueError, \
    ModelKeyError, UnauthorizedError, AccessDeniedError, NotFoundError, \
    UnexpectedArguments, NotAllowedError
from common.extensions import db


class NoSettingsModuleSpecified(Exception):
    pass


class NoBlueprintException(Exception):
    pass


class NoExtensionException(Exception):
    pass


class NoCommandException(Exception):
    pass


class AppFactory:
    __app = None

    def __init__(self, settings='FLASK_SETTINGS'):
        self.settings = os.environ.get(settings, False)
        if not self.settings:
            raise NoSettingsModuleSpecified(
                'Path to settings module is not found'
            )

    def get_app(self, app_module_name, **kwargs):
        self.__app = Flask(app_module_name, **kwargs)
        self.__app.config.from_pyfile(self.settings)

        self.__register_converters()

        if not self.__app.config['DEBUG']:
            self.__app.logger.setLevel(logging.INFO)
            del self.__app.logger.handlers[:]

            log_frmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(log_frmt))
            self.__app.logger.addHandler(stream_handler)

        self.__bind_extensions()
        self.__register_blueprints()
        self.__register_commands()

        if 'EMAILS_MODULE' in self.__app.config:
            importlib.import_module(self.__app.config['EMAILS_MODULE'])

        return self.__app

    def __bind_extensions(self):
        for ext_path in self.__app.config.get('EXTENSIONS', ()):
            try:
                obj = self.__import_object(ext_path)
            except ImportError:
                raise NoExtensionException(f'No {ext_path} extension found')

            if hasattr(obj, 'init_app') and callable(obj.init_app):
                obj.init_app(self.__app)
            elif callable(obj):
                obj(self.__app)
            else:
                raise NoExtensionException(
                    f'{ext_path} extension has no init_app.'
                )

            ext_name = ext_path.split('.')[-1]
            if ext_name not in self.__app.extensions:
                self.__app.extensions[ext_name] = obj

    def __register_blueprints(self):
        for blueprint_path in self.__app.config.get('BLUEPRINTS', ()):
            try:
                obj = self.__import_object(blueprint_path)
                self.__app.register_blueprint(obj)

            except ImportError:
                raise NoExtensionException(
                    f'No {blueprint_path} blueprint found'
                )

    def __register_commands(self):
        for commands_path in self.__app.config.get('COMMANDS', ()):
            try:
                obj = self.__import_object(commands_path)
                obj(self.__app)

            except ImportError:
                raise NoCommandException(f'No {commands_path} command found')

    def __register_converters(self):
        for name, path in self.__app.config.get('CONVERTERS', ()):
            try:
                converter = self.__import_object(path)
                self.__app.url_map.converters[name] = converter

            except ImportError:
                raise NoCommandException(f'No {name} converter found')

    @staticmethod
    def __import_object(path):
        module_name, object_name = path.rsplit('.', 1)
        mod = importlib.import_module(module_name)
        if not hasattr(mod, object_name):
            raise ImportError

        return getattr(mod, object_name)


# noinspection PyUnusedLocal
def create_app(script_info=None):
    load_dotenv()

    app = AppFactory().get_app(__name__)

    @app.before_request
    def before_request():
        g.start = time.time()

    @app.after_request
    def after_request(response):
        diff = time.time() - g.start
        app.logger.debug(f'Request finished in {diff}')

        return response

    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db)

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

        if not app.config['DEBUG'] and not (
                isinstance(error, AppException) and
                not isinstance(error, UnexpectedArguments)):
            errors_text = default_text

        if status == 500:
            app.logger.error(errors_text, exc_info=True)

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

        if isinstance(error, (NotFoundError, UnexpectedArguments,)):
            return app_error_response(error, 404, 'Not found')

        if isinstance(error, NotAllowedError):
            return app_error_response(error, 405, 'Method not allowed')

        if isinstance(error, HTTPException):
            return app_error_response(error, error.code, error.name)

        return app_error_response(error, 500, 'Unknown error')

    if app.config['DEBUG_SQL']:
        # noinspection PyUnusedLocal
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context,
                                  executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            app.logger.debug(f'Start Query: {statement}. '
                             f'With parameters: {parameters}')

        # noinspection PyUnusedLocal
        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context,
                                 executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            app.logger.debug(f'Query Complete. Total Time: {str(total)}\n')

    return app
