import os

BLUEPRINTS = (
    'apps.users.urls.bp',
    'general.urls.bp',
)

COMMANDS = (
    'apps.users.commands.users_group',
)

DEBUG_SQL = os.environ.get('FLASK_DEBUG', 'false') == 'true'

EXTENSIONS = (
    'extensions.db',
    'extensions.migrate',
)

JWTAUTH_SETTINGS = {
    'EXPIRES': 14
}

SECRET_KEY = 'kjbnKU&TSX^&TAd()U*(uo27893yrh36784f5$Y%^F%^$fw67fyohzlcSd3g7'

SQLALCHEMY_DATABASE_URI = 'postgresql://flask_api_user:flask_api_password@db/flask_api_db'  # nopep8
SQLALCHEMY_TRACK_MODIFICATIONS = False
