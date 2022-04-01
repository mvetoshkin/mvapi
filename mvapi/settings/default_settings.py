import os


class DefaultSettings:
    DEBUG = False
    DEBUG_SQL = False
    ENV = 'production'
    ERRORS_PATH = '.errors'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # noinspection PyPep8Naming
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.DB_URI

    def __getattr__(self, item):
        if item in os.environ:
            return os.environ[item]
        raise KeyError
