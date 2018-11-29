import importlib
import logging
import os

from flask import Flask
from flask.sessions import SessionMixin, SessionInterface


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
        self.__app.session_interface = NoSessionInterface()

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

        return self.__app

    def __bind_extensions(self):
        for ext_path in self.__app.config.get('EXTENSIONS', ()):
            try:
                obj = self.__import_object(ext_path)
            except ImportError:
                raise NoExtensionException(f'No {ext_path} extension found')

            if hasattr(obj, 'init_app'):
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


class NoSession(dict, SessionMixin):
    pass


class NoSessionInterface(SessionInterface):
    def open_session(self, app, request):
        return NoSession()

    def save_session(self, app, session, response):
        pass
