import click

from .set_user import set_user


@click.group()
def user():
    pass


user.add_command(set_user)
