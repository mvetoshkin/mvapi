import click

from mvapi.libs.logger import init_logger
from mvapi.libs.misc import import_object
from mvapi.settings import settings
from .migration import migration
from .run_temp_script import run_temp_script
from .user import user
from .web import web

version = import_object(f'{settings.APP_NAME}.version.version')


@click.group()
@click.version_option(version)
@click.option('--verbosity', is_flag=True, default=settings.DEBUG,
              help='Show debug log')
def cli(verbosity):
    init_logger(verbosity)


cli.add_command(migration)
cli.add_command(run_temp_script)
cli.add_command(user)
cli.add_command(web)
