import os

from dotenv import load_dotenv

from mvapi.libs.exceptions import NoSettingsModuleSpecified
from mvapi.libs.misc import import_object


def get_settings():
    config_file = os.environ.get('MVAPI_CONFIG', False)

    if config_file:
        if config_file.startswith('~'):
            config_file = os.path.expanduser(config_file)
        config_file = os.path.abspath(config_file)

        if os.path.exists(config_file):
            load_dotenv(config_file)

    app_settings = os.environ.get('SETTINGS')
    if not app_settings:
        raise NoSettingsModuleSpecified(
            'Path to settings module is not found'
        )

    settings_obj = import_object(app_settings)
    settings_obj.APP_NAME = app_settings.partition('.')[0]

    return settings_obj()


settings = get_settings()
