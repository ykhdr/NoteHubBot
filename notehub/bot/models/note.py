from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from bot.models import Base


class Note(Base):
    __table__ = 'notes'

    __note_id = Column(Integer, primary_key=True)
    __name = Column(String)
    __content = Column(String)
    __dir_id = Column(Integer, ForeignKey('directories.dir_id'))
    __user_id = Column(Integer, ForeignKey('users.user_id'))

    __dir = relationship('Directory', back_populates='notes')
    __user = relationship('User', back_populates='notes')

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
