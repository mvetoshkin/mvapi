import importlib
import os
import re
from datetime import datetime
from uuid import uuid4

import inflect
import shortuuid
from sqlalchemy import and_, Column, DateTime, inspect, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import ColumnProperty, Query, RelationshipProperty

import mvapi.web.models
from mvapi.libs.database import db
from mvapi.libs.exceptions import NotFoundError, ModelKeyError
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
        return self.get_by(id_=ident)

    def get_by(self, **kwargs):
        return self.filter_by(**kwargs).one()

    def apply_args(self, limit=None, offset=None, sort=None, filters=None):
        query = self

        if filters:
            query = query.filter(and_(*filters))

        if sort:
            query = query.order_by(*sort)

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query


class BaseModel(declarative_base()):
    __abstract__ = True

    __plural = None

    name_prefix = None
    default_sort = None
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
    def plural_type(self):
        if not self.__plural:
            text = ' '.join(self.type_.split('_'))
            plural = inflect.engine().plural(text)
            self.__plural = '_'.join(plural.split(' ')).lower()

        return self.__plural.lower() if self.__plural else self.type_

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

    @classmethod
    def get_sort_fields(cls, sort: str = None):
        if not sort:
            if not cls.default_sort:
                return cls.created_date.desc()
            return cls.default_sort

        sort_items = []
        sort_cols = set()

        for item in sort.split(','):
            asc = True
            if item.startswith('-'):
                asc = False
                item = item[1:]

            nulls_first = True
            parts = item.split(':')
            if len(parts) == 2:
                if parts[1].lower() == 'last':
                    nulls_first = False
                item = parts[0]

            if item.lower() == 'id':
                item = 'id_'

            func = getattr(cls, f'get_{item}_sort_column', None)
            if not func:
                sort_cols.add(item)

            sort_items.append({
                'asc': asc,
                'nulls_first': nulls_first,
                'column': func or item,
            })

        if sort_cols & cls.available_columns != sort_cols:
            raise ModelKeyError

        order_fields = []
        for item in sort_items:
            column = item['column']
            if callable(column):
                columns = column()
            else:
                columns = [getattr(cls, item['column'])]

            for column in columns:
                column = column.asc() if item['asc'] else column.desc()
                column = (column.nullsfirst() if item['nulls_first']
                          else column.nullslast())
                order_fields.append(column)

        return order_fields


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
