from datetime import datetime

import bcrypt
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import validates
from validate_email import validate_email

from general.exceptions import NotFoundError, AppValueError
from general.models import BaseModel


class User(BaseModel):
    email: Column = Column(String(64), nullable=False, unique=True, index=True)
    password: Column = Column(String(64), nullable=False)
    deleted: Column = Column(DateTime, index=True)
    is_admin: Column = Column(Boolean, nullable=False, default=False)
    first_name: Column = Column(String(50))
    last_name: Column = Column(String(50))

    def __repr__(self):
        return f'<Email: {self.email}>'

    @property
    def full_name(self):
        names = []

        if self.first_name:
            names.append(self.first_name)
        if self.last_name:
            names.append(self.last_name)

        if not names:
            names = ['User', str(self.id_)]

        return ' '.join(names)

    @property
    def salt(self):
        return self.email

    # noinspection PyUnusedLocal
    @validates('email')
    def validate_email(self, key, email):
        is_valid = validate_email(email)
        if not is_valid:
            raise AppValueError('Email is not valid')

        return email

    # noinspection PyUnusedLocal
    @validates('password')
    def validate_password(self, key, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()

    def disable(self):
        self.deleted = datetime.utcnow()

    def passwords_matched(self, password):
        if not self.password:
            return False
        return bcrypt.checkpw(password.encode(), self.password.encode())

    @classmethod
    def get_auth_user(cls, id_):
        query = cls.session.query(cls)
        return cls.get(id_=id_, query=query)

    @classmethod
    def find_by_email(cls, email, check_all=False):
        query = cls.session.query(cls) if check_all else cls.get_query()
        query = query.filter(cls.email == email)

        user = query.first()
        if not user:
            raise NotFoundError

        return user
