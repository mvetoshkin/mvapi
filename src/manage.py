import time

import click
import flask
from flask.cli import FlaskGroup
from sqlalchemy import event
from sqlalchemy.engine import Engine

from extensions import db
from helpers.appfactory import AppFactory


# noinspection PyUnusedLocal
def create_app(script_info=None):
    app = AppFactory().get_app(__name__)

    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db)

    @app.teardown_appcontext
    def teardown_appcontext(exception):
        if exception:
            db.session.rollback()
        else:
            db.session.commit()

        db.session.remove()

    # noinspection PyUnusedLocal
    @event.listens_for(Engine, 'before_cursor_execute')
    def before_cursor_execute(conn, cursor, statement, parameters, context,
                              executemany):
        if not app.config['DEBUG_SQL']:
            return

        conn.info.setdefault('query_start_time', []).append(time.time())
        print('Start Query: {}. With parameters: {}'.format(
            statement, parameters
        ))

    # noinspection PyUnusedLocal
    @event.listens_for(Engine, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, parameters, context,
                             executemany):
        if not app.config['DEBUG_SQL']:
            return

        total = time.time() - conn.info['query_start_time'].pop(-1)
        print('Query Complete. Total Time: ' + str(total))
        print('')

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """This is a management script for the application."""


if __name__ == '__main__':
    cli()
