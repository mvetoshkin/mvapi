import importlib

import click
from dateutil.parser import parse
from jinja2 import Environment, PackageLoader, PrefixLoader


def import_object(path):
    module_name, object_name = path.rsplit('.', 1)
    mod = importlib.import_module(module_name)
    if not hasattr(mod, object_name):
        raise ImportError

    return getattr(mod, object_name)


def render_template(template_name, data):
    from mvapi.settings import settings

    prefixes = {'mvapi': PackageLoader('mvapi', 'templates')}
    for k, v in settings.TEMPLATE_LOADERS.items():
        prefixes[k] = PackageLoader(*v)

    env = Environment(loader=PrefixLoader(prefixes))
    tmpl = env.get_template(template_name)
    return tmpl.render(data)


# noinspection PyPep8Naming
class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


# noinspection PyUnusedLocal
def validate_date_arg(ctx, param, value):
    if not value:
        return None

    try:
        return parse(value)
    except ValueError:
        raise click.BadParameter('value cannot be parsed')
