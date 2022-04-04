import importlib
import os

from jinja2 import Template

import mvapi


def import_object(path):
    module_name, object_name = path.rsplit('.', 1)
    mod = importlib.import_module(module_name)
    if not hasattr(mod, object_name):
        raise ImportError

    return getattr(mod, object_name)


def render_template(template_name, data):
    filename = os.path.join(
        os.path.dirname(mvapi.__file__),
        'templates',
        f'{template_name}.tmpl'
    )

    with open(filename, 'rt') as tmpl_file:
        tmpl = Template(tmpl_file.read())
        result = tmpl.render(data)

    return result


# noinspection PyPep8Naming
class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)
