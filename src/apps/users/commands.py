import click

from .models import User


def users_group(app):
    @app.cli.group()
    def users():
        """Users commands."""
        pass

    @users.command('createadmin')
    @click.option('--email', default=None, help='user email')
    @click.option('--password', default=None, help='user password')
    def add_admin_user(email, password):
        """Create an admin user."""

        u = User.create(email=email, password=password, is_admin=True)
        print(u)
