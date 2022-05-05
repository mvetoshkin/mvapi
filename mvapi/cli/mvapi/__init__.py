import click

from mvapi.version import version
from .init_project import init_project


@click.group()
@click.version_option(version)
def cli():
    pass


cli.add_command(init_project)
