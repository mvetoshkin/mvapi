import click
from alembic.command import downgrade

from .utils import DIRECTORY, get_config


@click.command('downgrade')
@click.option('--directory', default=DIRECTORY,
              help='path to the migrations directory')
@click.option('--revision', default='-1',
              help='revision target or range for --sql mode')
@click.option('--sql', is_flag=True,
              help='dump the script out as a SQL string; when specified, '
                   'the script is dumped to stdout')
@click.option('--tag', help='an arbitrary tag that can be intercepted by '
                            'custom `env.py` scripts')
def downgrade_(directory, revision, sql, tag):
    """Revert to a previous version"""

    if sql and revision == '-1':
        revision = 'head:-1'

    config = get_config(directory)
    downgrade(config, revision, sql=sql, tag=tag)
