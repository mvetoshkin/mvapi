import json
import time

import click
from flask.cli import FlaskGroup
from sqlalchemy import event
from sqlalchemy.engine.base import Engine

from extensions import db
from helpers.appfactory import AppFactory


# noinspection PyUnusedLocal
def create_app(script_info=None):
    app = AppFactory().get_app(__name__)

    def app_error_response(text, code, error):
        error_orig_text = str(error)

        if code == 500:
            app.logger.error(error_orig_text, exc_info=True)

        error_text = error_orig_text if app.config['DEBUG'] else text

        return json.dumps({'error': error_text}), code, {
            'Content-Type': 'application/json; charset=utf-8'
        }

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

    @app.errorhandler(403)
    def error_403_handler(error):
        return app_error_response('access denied', error.code, error)

    @app.errorhandler(404)
    def error_404_handler(error):
        return app_error_response('not found', error.code, error)

    @app.errorhandler(500)
    def error_500_handler(error):
        return app_error_response('unknown error', error.code, error)

    if app.config['DEBUG_SQL']:
        # noinspection PyUnusedLocal
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context,
                                  executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            app.logger.debug(f'Start Query: {statement}. '
                             f'With parameters: {parameters}')

        # noinspection PyUnusedLocal
        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context,
                                 executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            app.logger.debug(f'Query Complete. Total Time: {str(total)}\n')

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """This is a management script for the application."""


if __name__ == '__main__':
    cli()

else:
    application = create_app()
