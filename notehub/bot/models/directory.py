from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Directory:
    __table__ = 'directories'

    __dir_id = Column(Integer, primary_key=True)
    __name = Column(String)
    __user_id = Column(Integer, ForeignKey('users.user_id'))
    __parent_dir_id = Column(Integer, ForeignKey('directories.dir_id'))

    __user = relationship('User', back_populates='directory')
    __parent_dir = relationship('Directory', back_populates='directory')

    def __init__(self, name, user, parent_dir):
        self.__name = name
        self.__user = user
        self.__parent_dir = parent_dir

    def get_id(self):
        return self.__dir_id

    def get_name(self):
        return self.__name

    def get_user(self):
        return self.__user

    def get_parent_dir(self):
        return self.__parent_dir
