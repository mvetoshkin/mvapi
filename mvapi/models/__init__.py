import importlib
import os
import re
from datetime import datetime
from uuid import uuid4

import shortuuid
from sqlalchemy import Column, DateTime, inspect, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import ColumnProperty, Query, RelationshipProperty

import mvapi.web.models
from mvapi.libs.database import db
from mvapi.libs.exceptions import NotFoundError
from mvapi.libs.misc import classproperty
from mvapi.settings import settings


class BaseQuery(Query):
    def one(self, *filters):
        try:
            if filters:
                return self.filter(*filters).one()
            else:
                return super(BaseQuery, self).one()
        except NoResultFound:
            raise NotFoundError

    def get(self, ident):
        obj = super(BaseQuery, self).get(ident)
        if not obj:
            raise NotFoundError
        return obj

    def get_by(self, **kwargs):
        return self.filter_by(**kwargs).one()


class BaseModel(declarative_base()):
    __abstract__ = True

    name_prefix = None
    query = db.session.query_property(query_cls=BaseQuery)

    id_: Column = Column(
        'id',
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    created_date: Column = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    modified_date: Column = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id_}>'

    @declared_attr
    def __tablename__(self):
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', self.__name__).lower()
        if self.name_prefix:
            name = self.name_prefix + '_' + name
        return name

    @property
    def type_(self):
        return self.__table__.name.lower()

    @property
    def short_id(self):
        return shortuuid.encode(self.id_)

    @classproperty
    def available_columns(self):
        return {key for key, value in inspect(self).mapper.attrs.items()
                if isinstance(value, ColumnProperty)}

    @classproperty
    def available_relationships(self):
        attrs = inspect(self).mapper.attrs
        return {key: value.local_columns for key, value in attrs.items()
                if isinstance(value, RelationshipProperty)}

    @classproperty
    def relationship_keys(self):
        rels = self.available_relationships
        keys = set(rels.keys())

        for fields in rels.values():
            keys |= {field.name for field in fields
                     if field.name in self.available_columns}

        return keys

    @classproperty
    def required_keys(self):
        keys = set()

        for key in self.available_columns:
            attr = getattr(self, key)
            if hasattr(attr, 'nullable') and not attr.nullable:
                keys.add(key)

        for key, value in self.available_relationships.items():
            for column in value:
                if column.name in keys:
                    keys.add(key)

        return keys

    @classmethod
    def create(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        db.session.add(obj)
        db.session.flush()
        return obj

    def delete(self):
        db.session.delete(self)
        db.session.flush()


def import_models():
    models = [__package__] + \
             [mvapi.web.models.__package__] + \
             settings.MODELS

    for model_str in models:
        model = importlib.import_module(model_str)
        for file in os.listdir(os.path.dirname(model.__file__)):
            if not file.startswith('__') and file.endswith('.py'):
                name = file.rpartition('.')[0]
                importlib.import_module(f'{model.__package__}.{name}')
