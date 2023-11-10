from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from bot.models import Base
from bot.models.directory import Directory
from bot.models.user import User


class CurrentUserDirectory(Base):
    __tablename__ = 'current_user_directory'

    chat_id = Column(BigInteger, ForeignKey('users.chat_id'), primary_key=True)
    dir_id = Column(BigInteger, ForeignKey('directories.id'), nullable=False)

    user = relationship(User, foreign_keys=chat_id)
    dir = relationship(Directory, foreign_keys=dir_id)

    def __init__(self, chat_id, dir_id):
        self.chat_id = chat_id
        self.dir_id = dir_id
