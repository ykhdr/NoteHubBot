from sqlalchemy import Integer, Column, BigInteger
from sqlalchemy.orm import relationship

from bot.models import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=False)

    # notes = relationship( Note, back_populates='user')
    # directories = relationship(Directory, back_populates='user')
    #
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id
