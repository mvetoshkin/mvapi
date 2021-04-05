import importlib
import os

from dotenv import load_dotenv

from mvapi.common.exceptions import NoSettingsModuleSpecified


def import_object(path):
    module_name, object_name = path.rsplit('.', 1)
    mod = importlib.import_module(module_name)
    if not hasattr(mod, object_name):
        raise ImportError

    return getattr(mod, object_name)


def get_app_name():
    return os.environ['MVAPI_APP_NAME']


def get_app_path():
    app_name = get_app_name()
    module = importlib.import_module(app_name)
    return os.path.dirname(module.__file__)


def get_settings():
    app_name = get_app_name()
    path = get_app_path()
    load_dotenv(os.path.join(path, '.env'))

    settings = os.environ.get('MVAPI_SETTINGS', False)
    if not settings:
        raise NoSettingsModuleSpecified(
            'Path to settings module is not found'
        )

    obj = import_object(f'{app_name}.{settings}')
    return obj()
