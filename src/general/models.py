from datetime import datetime
import time

from sqlalchemy import Column, Integer, DateTime, inspect, event
from sqlalchemy.engine import Engine

from extensions import db
from general.exceptions import NotFoundError
from general.utils import classproperty


class BaseModel(db.Model):
    __abstract__ = True

    id_ = Column('id', Integer, primary_key=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    @classproperty
    def session(self):
        return db.session

    def populate(self, **kwargs):
        columns = set(inspect(self).mapper.columns.keys())
        columns -= {'id_', 'created_date', 'modified_date'}

        for attr in kwargs.keys():
            if attr in columns:
                setattr(self, attr, kwargs[attr])
            else:
                raise KeyError("Attribute '{}' doesn't exist".format(attr))

        return self

    def update(self, **kwargs):
        self.populate(**kwargs)
        self.modified_date = datetime.utcnow()
        self.session.flush()
        return self

    def delete(self):
        self.session.delete(self)
        self.session.flush()

    @classmethod
    def create(cls, **kwargs):
        record = cls()
        record.populate(**kwargs)

        cls.session.add(record)
        cls.session.flush()

        return record

    @classmethod
    def get(cls, id_):
        query = cls.session.query(cls)
        query = query.filter(cls.id_ == id_)

        record = query.first()
        if not record:
            raise NotFoundError

        return record

    @classmethod
    def find(cls, ids):
        query = cls.session.query(cls)
        query = query.filter(cls.id_.in_(ids))
        return query.all()

    @classmethod
    def all(cls):
        query = cls.session.query(cls)
        return query.all()
