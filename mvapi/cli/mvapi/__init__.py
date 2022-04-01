import click

from mvapi.libs.logger import init_logger
from mvapi.version import version
from .init_project import init_project


@click.group()
@click.version_option(version)
@click.option('--verbosity', is_flag=True, default=False, help='show debug log')
def cli(verbosity):
    init_logger(verbosity)


cli.add_command(init_project)
