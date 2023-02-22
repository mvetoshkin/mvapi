import time

from sqlalchemy import create_engine, event
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mvapi.settings import settings
from mvapi.web.libs.logger import logger


class DB:
    __instance = None
    session = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DB, cls).__new__(cls)

            engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
            cls.__instance.session = scoped_session(
                sessionmaker(autocommit=False, bind=engine)
            )

        return cls.__instance

    def __init__(*args, **kwargs):
        if settings.DEBUG_SQL:
            # noinspection PyUnusedLocal
            @event.listens_for(Engine, 'before_cursor_execute')
            def before_cursor_execute(conn, cursor, statement, parameters,
                                      context, executemany):
                t = conn.info.setdefault('query_start_time', [])
                t.append(time.time())
                logger.debug(f'Start Query: {statement}. '
                             f'With parameters: {parameters}')

            # noinspection PyUnusedLocal
            @event.listens_for(Engine, 'after_cursor_execute')
            def after_cursor_execute(conn, cursor, statement, parameters,
                                     context, executemany):
                total = time.time() - conn.info['query_start_time'].pop(-1)
                logger.debug(f'Query Complete. Total Time: {str(total)}\n')


db = DB()
