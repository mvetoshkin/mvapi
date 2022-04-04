import logging

import click

from mvapi.web.models.user import User

logger = logging.getLogger(__name__)


@click.command('update-user')
@click.option('--email', required=True, help='user email')
@click.option('--is-admin', is_flag=True, help='make user an admin')
@click.password_option(help='user password')
def update_user(email, password, is_admin):
    """Update a user."""

    user = User.get_by_email(email=email)

    if password:
        user.password = password

    if is_admin:
        user.is_admin = is_admin

    logger.info(f'User {user} updated')
