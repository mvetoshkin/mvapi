import click

from .run import run_


@click.group()
def web():
    pass


web.add_command(run_)
