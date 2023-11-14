from sqlalchemy import Column, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, backref

from bot.models.entities.entity import Entity
from bot.models.entities.storage import Storage
from bot.models.entities.user import User


class Directory(Entity.getEntityClassInstance(), Storage):
    __tablename__ = 'directories'

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    chat_id = Column(BigInteger, ForeignKey('users.chat_id'))
    parent_dir_id = Column(BigInteger, ForeignKey('directories.id', ondelete='cascade'))

    user = relationship(User, backref=backref('directory', cascade='all,delete'))
    parent_dir = relationship('Directory', backref=backref('directory', cascade='all,delete-orphan'),
                              remote_side='Directory.id', cascade='all,delete-orphan', passive_deletes=True,
                              single_parent=True)

    def __init__(self, name, user_id, parent_dir_id):
        self.name = name
        self.chat_id = user_id
        self.parent_dir_id = parent_dir_id

    def get_id(self):
        return self.dir_id

    def get_name(self):
        """Overrides"""
        return self.name

    def get_user(self):
        return self.chat_id

    def get_parent_dir(self):
        return self.parent_dir_id
