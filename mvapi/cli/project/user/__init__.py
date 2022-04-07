import click

from .create_user import create_user
from .update_user import update_user


@click.group()
def user():
    """Manage users"""
    pass


user.add_command(create_user)
user.add_command(update_user)
