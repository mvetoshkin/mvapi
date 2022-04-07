import click
from alembic.command import init

from .utils import DIRECTORY, get_config


@click.command('init')
@click.option('--directory', default=DIRECTORY,
              help='path to the migrations directory')
@click.option('--template', default='generic',
              help='name of the migration environment template to use')
def init_(directory, template):
    """Initialize a new scripts directory"""

    config = get_config(directory)
    init(config, directory, template=template)
