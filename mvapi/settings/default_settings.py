import os


class DefaultSettings:
    BLUEPRINTS = []
    CONVERTERS = []
    DEBUG = False
    DEBUG_SQL = False
    EMAILS_MODULE = None
    ENV = 'production'
    ERRORS_PATH = '.errors'
    EXTENSIONS = []
    MODELS = []
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # noinspection PyPep8Naming
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.DB_URI

    def __getattr__(self, item):
        if item in os.environ:
            return os.environ[item]
        raise KeyError
