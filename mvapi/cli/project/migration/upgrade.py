import click
from alembic.command import upgrade

from .utils import DIRECTORY, get_config


@click.command('upgrade')
@click.option('--directory', default=DIRECTORY,
              help='path to the migrations directory')
@click.option('--revision', default='head',
              help='revision target or range for --sql mode')
@click.option('--sql', is_flag=True,
              help='dump the script out as a SQL string; when specified, '
                   'the script is dumped to stdout')
@click.option('--tag', help='an arbitrary tag that can be intercepted by '
                            'custom `env.py` scripts')
def upgrade_(directory, revision, sql, tag):
    """Upgrade to a later version"""

    config = get_config(directory)
    upgrade(config, revision, sql=sql, tag=tag)
