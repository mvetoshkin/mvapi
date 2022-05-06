import os
import sys


class DefaultSettings:
    API_LOGGER_NAME = 'api'
    BLUEPRINTS = []
    CONVERTERS = []
    DEBUG = False
    DEBUG_SQL = False
    EMAILS_MODULE = None
    ENV = 'production'
    ERRORS_PATH = '.errors'
    EXTENSIONS = []
    JWTAUTH_SETTINGS = {}
    LIMIT = 15
    MIGRATIONS_EXCLUDE_TABLES = tuple()
    MODELS = []
    SERIALIZERS = []
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SYSLOG = False
    TEMPLATE_LOADERS = {}
    VIEWS = []

    # noinspection PyPep8Naming
    @property
    def LOGGING(self):
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s %(name)s %(levelname)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console'],
                    'level': 'DEBUG' if self.DEBUG else 'INFO'
                }
            }
        }

        if self.SYSLOG:
            if self.SYSLOG is not True:
                syslog_addr = self.SYSLOG
            else:
                if sys.platform == 'darwin':
                    syslog_addr = '/var/run/syslog'
                elif sys.platform == 'linux':
                    syslog_addr = '/dev/log'
                else:
                    syslog_addr = ('localhost', 514)

            config['formatters']['syslog'] = {
                'format': '%(name)s: %(message)s'
            }

            config['handlers']['syslog'] = {
                'formatter': 'syslog',
                'class': 'logging.handlers.SysLogHandler',
                'level': 'INFO',
                'address': syslog_addr
            }

            root_logger = config['loggers']['']
            root_logger['handlers'].clear()
            root_logger['handlers'].append('syslog')

        return config

    # noinspection PyPep8Naming
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.DB_URI

    # noinspection PyPep8Naming
    @property
    def ROOT_LOGGER_NAME(self):
        return self.APP_NAME

    def __getattr__(self, item):
        if item in os.environ:
            return os.environ[item]
        raise KeyError
