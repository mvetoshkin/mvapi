import os


class DefaultSettings:
    DEBUG = False
    DEBUG_SQL = False
    ENV = 'production'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # noinspection PyPep8Naming
    @property
    def SECRET_KEY(self):
        return os.environ['MVAPI_SECRET_KEY']

    # noinspection PyPep8Naming
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return 'postgresql://{}:{}@{}/{}'.format(
            os.environ['DB_USER'], os.environ['DB_PASSWORD'],
            os.environ['DB_HOST'], os.environ['DB_NAME'])
