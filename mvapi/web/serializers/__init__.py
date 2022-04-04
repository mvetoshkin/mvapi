import importlib
import os

from mvapi.settings import settings
from mvapi.web.serializers.base import BaseSerializer

RESOURCE_SERIALIZERS = {}


def import_serializers():
    views = [__package__] + settings.SERIALIZERS

    for view_str in views:
        view = importlib.import_module(view_str)
        for file in os.listdir(os.path.dirname(view.__file__)):
            if not file.startswith('__') and file.endswith('.py'):
                name = file.rpartition('.')[0]
                mod = importlib.import_module(f'{view.__package__}.{name}')
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if type(attr) == type and \
                            issubclass(attr, BaseSerializer) and \
                            attr != BaseSerializer:
                        RESOURCE_SERIALIZERS[attr.resource_type] = attr
