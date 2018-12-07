import logging

import sentry_sdk
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from general.query import BaseQuery

cors = CORS()
db = SQLAlchemy(query_class=BaseQuery)
login_manager = LoginManager()
migrate = Migrate(db=db)


# noinspection PyUnusedLocal
def sentry(app):
    sentry_logging = LoggingIntegration(
        level=logging.ERROR,
        event_level=logging.ERROR
    )

    sentry_sdk.init(integrations=[sentry_logging, FlaskIntegration()])
