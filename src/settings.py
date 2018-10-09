import os


BLUEPRINTS = (
    'apps.users.urls.bp',
    'general.urls.bp',
)

COMMANDS = (
    'apps.users.commands.users_group',
)

CONVERTERS = (
    ('uritemplate', 'converters.URITemplateConverter'),
)

CORS_EXPOSE_HEADERS = []
DEBUG = os.environ.get('FLASK_DEBUG', 'true') == 'true'
DEBUG_SQL = DEBUG

JWTAUTH_SETTINGS = {
    'EXPIRES': 14
}

MIGRATIONS_EXCLUDE_TABLES = ()
SECRET_KEY = os.environ['SECRET_KEY']

#####

EXTENSIONS = [
    'extensions.cors',
    'extensions.db',
    'extensions.migrate',

    # Flask login is used just for sentry, because sentry uses it for
    # getting information about a current user.
    'extensions.login_manager',
]

if not DEBUG and 'SENTRY_DNS' in os.environ:
    EXTENSIONS.append('extensions.sentry')

#####

SQLALCHEMY_DATABASE_URI = ('postgresql://{}:{}@{}/{}'.format(
    os.environ['DB_USER'], os.environ['DB_PASSWORD'], os.environ['DB_HOST'],
    os.environ['DB_NAME'])
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
