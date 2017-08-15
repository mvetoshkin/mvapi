from flask import url_for as uf


# noinspection PyPep8Naming
class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


def url_for(*args, **kwargs):
    if '_external' not in kwargs:
        kwargs['_external'] = True
    return uf(*args, **kwargs)
