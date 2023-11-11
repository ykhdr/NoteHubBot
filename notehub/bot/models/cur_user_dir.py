from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship, backref

from bot.models import Base
from bot.models.directory import Directory
from bot.models.user import User


class CurrentUserDirectory(Base):
    __tablename__ = 'current_user_directory'

    chat_id = Column(BigInteger, ForeignKey('users.chat_id', ondelete='cascade'), primary_key=True)
    dir_id = Column(BigInteger, ForeignKey('directories.id', ondelete='cascade'), nullable=False)

    user = relationship(User, backref=backref('cur_user_dir', cascade='all,delete'))
    dir = relationship(Directory, backref=backref('cur_user_dir'))

    def __init__(self, chat_id, dir_id):
        self.chat_id = chat_id
        self.dir_id = dir_id
