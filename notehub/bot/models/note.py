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
    user_id = Column(BigInteger, ForeignKey('users.id'))

    user = relationship(lambda: User, remote_side='users.id', backref='user_id')
    # user = relationship('User', back_populates='notes')
    dir = relationship(lambda: Directory, remote_side='directories.id', backref='dir_id')

    def __init__(self, name, content, user, dir):
        self.__name = name
        self.__content = content
        self.__user = user
        self.__dir = dir

    def get_id(self):
        return self.__note_id

    def get_name(self):
        return self.__name

    def get_content(self):
        return self.__content

    def get_user(self):
        return self.__user

    def get_dir(self):
        return self.__dir
