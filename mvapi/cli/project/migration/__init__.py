import click

from .downgrade import downgrade_
from .init import init_
from .revision import revision_
from .upgrade import upgrade_


@click.group()
def migration():
    """Database migrations"""

    pass


migration.add_command(downgrade_)
migration.add_command(init_)
migration.add_command(revision_)
migration.add_command(upgrade_)
