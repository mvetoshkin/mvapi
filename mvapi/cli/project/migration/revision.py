import click
from alembic.command import revision

from .utils import DIRECTORY, get_config


@click.command('revision')
@click.option('--directory', default=DIRECTORY,
              help='path to the migrations directory')
@click.option('--message', help='message to apply to the revision')
@click.option('--autogenerate', is_flag=True, default=True,
              help='autogenerate the script from the database')
@click.option('--sql', is_flag=True,
              help='dump the script out as a SQL string; when specified, '
                   'the script is dumped to stdout')
@click.option('--head', default='head',
              help='head revision to build the new revision upon as a parent')
@click.option('--splice', is_flag=True,
              help='the new revision should be made into a new head of its '
                   'own; is required when the given `head` is not itself a '
                   'head')
@click.option('--branch-label', help='label to apply to the branch')
@click.option('--version-path', help='symbol identifying a specific version '
                                     'path from the configuration')
@click.option('--rev_id', help='revision identifier to use instead of having '
                               'one generated')
def revision_(directory, message, autogenerate, sql, head, splice, branch_label,
              version_path, rev_id):
    """Create a new revision file"""

    config = get_config(directory)
    revision(config, message=message, autogenerate=autogenerate, sql=sql,
             head=head, splice=splice, branch_label=branch_label,
             version_path=version_path, rev_id=rev_id)
