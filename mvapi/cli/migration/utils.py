import os

from alembic.config import Config as AlembicConfig

DIRECTORY = 'migrations'


class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')


def get_config(directory):
    config = Config()
    config.config_file_name = os.path.join(directory, 'alembic.ini')

    return config
