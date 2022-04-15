import logging

import click

from mvapi.libs.exceptions import NotFoundError
from mvapi.web.models.user import User

logger = logging.getLogger(__name__)


@click.command('create-user')
@click.option('--email', required=True, help='user email')
@click.option('--is-admin', is_flag=True, help='make user an admin')
@click.password_option(help='user password', required=True)
def create_user(email, password, is_admin):
    """Create a user"""

    try:
        user = User.query.get_by(email=email)
        logger.info(f'User {user} exists')
        return
    except NotFoundError:
        pass

    user = User.create(email=email, password=password, is_admin=is_admin)
    logger.info(f'User {user} created')
