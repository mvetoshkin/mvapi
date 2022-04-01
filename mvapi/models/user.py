from sqlalchemy import Column, String, DateTime, Boolean

from mvapi.models import BaseModel


class User(BaseModel):
    email = Column(
        String(128),
        nullable=False,
        unique=True,
        index=True
    )

    password = Column(
        String(128),
        nullable=False
    )

    deleted = Column(
        DateTime,
        index=True,
        nullable=False,
        default=False
    )

    is_admin = Column(
        Boolean,
        nullable=False,
        default=False
    )

    name = Column(
        String(128)
    )
