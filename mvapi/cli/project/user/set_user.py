import click

from mvapi.models.user import User


@click.command()
def set_user():
    User.query.get(111)
    print('set_user')
