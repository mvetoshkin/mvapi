import bcrypt

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import validates
from validate_email import validate_email

from general.exceptions import NotFoundError
from general.models import BaseModel


class User(BaseModel):
    email = Column(String(64), nullable=False, unique=True, index=True)
    password = Column(String(64))
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_admin = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Email: {}>'.format(self.email)

    # noinspection PyUnusedLocal
    @validates('email')
    def validate_email(self, key, email):
        is_valid = validate_email(email)
        if not is_valid:
            raise ValueError('Email is not valid')

        return email

    # noinspection PyUnusedLocal
    @validates('password')
    def validate_password(self, key, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()

    def passwords_matched(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    @classmethod
    def find_by_email(cls, email):
        query = cls.session.query(cls)
        query = query.filter(cls.email == email)

        user = query.first()
        if not user:
            raise NotFoundError

        return user
