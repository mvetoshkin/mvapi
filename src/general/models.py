from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, Integer, DateTime, inspect, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import ColumnProperty, RelationshipProperty

from extensions import db
from general.exceptions import NotFoundError, BadRequestError
from general.utils import classproperty


class BaseModel(db.Model):
    __abstract__ = True
    __session = None

    id_: Column = Column('id', UUID(as_uuid=True), primary_key=True,
                         default=uuid4)
    created_date: Column = Column(DateTime, nullable=False,
                                  default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    default_sort = None

    @classproperty
    def session(self):
        return self.__session or db.session

    @classproperty
    def available_columns(self):
        return {key for key, value in inspect(self).mapper.attrs.items()
                if isinstance(value, ColumnProperty)}

    @classproperty
    def available_relationships(self):
        attrs = inspect(self).mapper.attrs
        return {key: value.local_columns for key, value in attrs.items()
                if isinstance(value, RelationshipProperty)}

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id_}>'

    def populate(self, **kwargs):
        used_columns = set()

        relationships = self.available_relationships
        for attr in kwargs:
            cols = relationships.get(attr)
            if cols:
                value = self.get_param_value(kwargs[attr])
                setattr(self, attr, value)
                for col in cols:
                    value = kwargs[attr].id_ if kwargs[attr] else None
                    setattr(self, col.key, value)
                used_columns.add(attr)

        columns = self.available_columns
        for attr in kwargs.keys():
            if attr in columns:
                value = self.get_param_value(kwargs[attr])
                setattr(self, attr, value)
                used_columns.add(attr)

        remaining_attrs = list(set(kwargs.keys()) - used_columns)
        if remaining_attrs:
            if len(remaining_attrs) == 1:
                raise KeyError(f'Attribute {remaining_attrs[0]} doesn\'t exist')
            else:
                attrs = ', '.join(remaining_attrs)
                raise KeyError(f'Attributes {attrs} don\'t exist')

        return self

    def delete(self):
        self.session.delete(self)
        self.session.flush()

    @classmethod
    def set_session(cls, session):
        cls.__session = session

    @classmethod
    def create(cls, **kwargs):
        record = cls()
        record.populate(**kwargs)

        cls.session.add(record)
        cls.session.flush()

        return record

    @classmethod
    def get_query(cls, *fields):
        if fields:
            return cls.session.query(*fields)
        return cls.session.query(cls)

    @classmethod
    def set_sort(cls, query, sort: str=None):
        if not sort:
            if not cls.default_sort:
                return query.order_by(cls.id_.desc())
            return query.order_by(*cls.default_sort)

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
            raise BadRequestError

        order_fields = []
        for item in sort_items:
            column = item['column']
            if callable(column):
                query, columns = column(query)
            else:
                columns = [getattr(cls, item['column'])]

            for column in columns:
                column = column.asc() if item['asc'] else column.desc()
                column = (column.nullsfirst() if item['nulls_first']
                          else column.nullslast())
                order_fields.append(column)

        return query.order_by(*order_fields)

    @classmethod
    def get(cls, id_, query=None):
        query = query or cls.get_query()
        query = query.filter(cls.id_ == id_)

        record = query.first()
        if not record:
            raise NotFoundError

        return record

    @classmethod
    def find(cls, ids, query=None):
        if not ids:
            return []

        query = query or cls.get_query()
        query = query.filter(cls.id_.in_(ids))
        items_idx = {item.id_: item for item in query.all()}

        items = []
        for id_ in ids:
            item = items_idx.get(id_)
            if item:
                items.append(item)

        return items

    @classmethod
    def all(cls, limit=30, offset=0, sort=None, as_count=False, query=None,
            filters: list=None):
        query = query or cls.get_query()

        if filters:
            query = query.filter(and_(*filters))

        query = cls.set_sort(query=query, sort=sort)

        if as_count:
            return query.count()

        if limit:
            query = query.limit(limit)
            query = query.offset(offset)

        return query.all()

    @staticmethod
    def get_param_value(param):
        if type(param) == str and len(param) == 0:
            return None
        return param
