import click

from mvapi.libs.logger import init_logger
from mvapi.libs.misc import import_object
from mvapi.settings import settings
from .migration import migration
from .user import user
from .web import web

version = import_object(f'{settings.APP_NAME}.version.version')


@click.group()
@click.version_option(version)
@click.option('--verbosity', is_flag=True, default=settings.DEBUG,
              help='show debug log')
def cli(verbosity):
    init_logger(verbosity)


cli.add_command(migration)
cli.add_command(user)
cli.add_command(web)
