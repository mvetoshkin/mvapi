import click

from .init_project import init_project


@click.group()
def mvapi():
    pass


mvapi.add_command(init_project)
