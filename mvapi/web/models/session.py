from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from mvapi.models import BaseModel


class Session(BaseModel):
    remote_ip: Column = Column(String(64))
    user_agent: Column = Column(String)
    user_id: Column = Column(String, ForeignKey('user.id', ondelete='CASCADE'),
                             index=True, nullable=False)

    user = relationship('User', lazy='joined', uselist=False)
