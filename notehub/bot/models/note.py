from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from bot.models import Base
from bot.models.directory import Directory
from bot.models.user import User


class Note(Base):
    __tablename__ = 'notes'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=True)
    dir_id = Column(BigInteger, ForeignKey('directories.id'))
    chat_id = Column(BigInteger, ForeignKey('users.id'))

    user = relationship(User, foreign_keys=chat_id)
    # user = relationship('User', back_populates='notes')
    dir = relationship(Directory, foreign_keys=dir_id)

    def __init__(self, name, content, user, dir):
        self.name = name
        self.content = content
        self.chat_id = user
        self.dir = dir

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_content(self):
        return self.content

    def get_user(self):
        return self.user

    def get_dir(self):
        return self.dir
