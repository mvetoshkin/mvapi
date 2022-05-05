import click

from mvapi.libs.misc import import_object
from mvapi.settings import settings
from .migration import migration
from .run_temp_script import run_temp_script
from .user import user
from .web import web

version = import_object(f'{settings.APP_NAME}.version.version')


@click.group()
@click.version_option(version)
def cli():
    pass


cli.add_command(migration)
cli.add_command(run_temp_script)
cli.add_command(user)
cli.add_command(web)
