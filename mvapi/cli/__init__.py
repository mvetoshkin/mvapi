import click

from mvapi.cli.migration import migration
from mvapi.cli.web import web


@click.group()
def cli():
    pass


cli.add_command(migration)
cli.add_command(web)
