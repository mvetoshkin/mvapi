import click

from .run import run_


@click.group()
def web():
    """Web server commands"""

    pass


web.add_command(run_)
