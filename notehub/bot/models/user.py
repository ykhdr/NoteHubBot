from sqlalchemy import Integer, Column
from sqlalchemy.orm import relationship

from bot.models import Base


class User(Base):
    __table__ = 'users'

    __user_id = Column(Integer, primary_key=True)

    __notes = relationship('Note', back_populates='user')

    def get_id(self):
        return self.__user_id
