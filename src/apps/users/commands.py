import click

from .models import User


def users_group(app):
    @app.cli.group()
    def users():
        """Users commands."""
        pass

    @users.command('create_admin')
    @click.option('--email', required=True, help='user email')
    @click.option('--password', required=True, help='user password')
    def create_admin(email, password):
        """Create an admin user."""

        u = User.create(email=email, password=password, is_admin=True)
        app.logger.info(u)
