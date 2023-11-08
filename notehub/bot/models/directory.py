from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from bot.models import Base
from bot.models.user import User


class Directory(Base):
    __tablename__ = 'directories'

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    chat_id = Column(BigInteger, ForeignKey('users.chat_id'))
    parent_dir_id = Column(BigInteger, ForeignKey('directories.id'))

    user = relationship(User, foreign_keys=chat_id)
    parent_dir = relationship('Directory', foreign_keys=parent_dir_id)

    # user = relationship(lambda: User, remote_side='users.id', backref='id')
    # parent_dir = relationship(lambda: Directory, remote_side='directories.id', backref='parent_dir_id')

    def __init__(self, name, user_id, parent_dir_id):
        self.name = name
        self.chat_id = user_id
        self.parent_dir_id = parent_dir_id

    def get_id(self):
        return self.dir_id

    def get_name(self):
        return self.name

    def get_user(self):
        return self.chat_id

    def get_parent_dir(self):
        return self.parent_dir_id
