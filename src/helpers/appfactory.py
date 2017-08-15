import importlib
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
    app = None

    def __init__(self, settings='FLASK_SETTINGS'):
        self.settings = os.environ.get(settings, False)
        if not self.settings:
            raise NoSettingsModuleSpecified(
                'Path to settings module is not found'
            )

    def get_app(self, app_module_name, **kwargs):
        self.app = Flask(app_module_name, **kwargs)
        self.app.config.from_pyfile(self.settings)
        self.app.session_interface = NoSessionInterface()

        self.__bind_extensions()
        self.__register_blueprints()
        self.__register_commands()

        return self.app

    def __bind_extensions(self):
        for ext_path in self.app.config.get('EXTENSIONS', ()):
            try:
                obj = self.__import_object(ext_path)
            except ImportError:
                raise NoExtensionException(
                    'No {} extension found'.format(ext_path)
                )

            if hasattr(obj, 'init_app'):
                obj.init_app(self.app)
            elif callable(obj):
                obj(self.app)
            else:
                raise NoExtensionException(
                    '{} extension has no init_app.'.format(ext_path)
                )

    def __register_blueprints(self):
        for blueprint_path in self.app.config.get('BLUEPRINTS', ()):
            try:
                obj = self.__import_object(blueprint_path)
                self.app.register_blueprint(obj)

            except ImportError:
                raise NoExtensionException(
                    'No {} blueprint found'.format(blueprint_path)
                )

    def __register_commands(self):
        for commands_path in self.app.config.get('COMMANDS', ()):
            try:
                obj = self.__import_object(commands_path)
                obj(self.app)

            except ImportError:
                raise NoCommandException(
                    'No {} command found'.format(commands_path)
                )

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
