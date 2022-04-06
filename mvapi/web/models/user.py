import bcrypt
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import validates, relationship
from validate_email import validate_email

from mvapi.models import BaseModel, BaseQuery
from mvapi.web.libs.exceptions import AppValueError


class User(BaseModel):
    email = Column(String(128), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    deleted = Column(DateTime, index=True, default=None)
    is_admin = Column(Boolean, nullable=False, default=False)
    name = Column(String(128))

    sessions = relationship('Session', lazy='dynamic', viewonly=True,
                            query_class=BaseQuery)

    def __repr__(self):
        return f'<Email: {self.email}>'

    @property
    def salt(self):
        return self.email

    # noinspection PyUnusedLocal
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            return email

        if not validate_email(email):
            raise AppValueError('Email is not valid')

        return email.lower()

    # noinspection PyUnusedLocal
    @validates('password')
    def validate_password(self, key, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()

    def passwords_matched(self, password):
        if not self.password:
            return False
        return bcrypt.checkpw(password.encode(), self.password.encode())
