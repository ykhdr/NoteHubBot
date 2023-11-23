from sqlalchemy import Column, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from bot.models.entities.directory import Directory
from bot.models.entities.entity import Entity
from bot.models.entities.storage import Storage
from bot.models.entities.user import User


class Note(Entity.get_entity_class_instance(), Storage):
    __tablename__ = 'notes'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    name: Column = Column(String(30), nullable=False)
    content = Column(String(4096), nullable=True)
    dir_id = Column(BigInteger, ForeignKey('directories.id'))
    chat_id = Column(BigInteger, ForeignKey('users.chat_id'))

    user = relationship(User, foreign_keys=chat_id, lazy='joined')
    dir = relationship(Directory, foreign_keys=dir_id, lazy='joined')

    def __init__(self, name, content, chat_id, dir_id):
        self.name = name
        self.content = content
        self.chat_id = chat_id
        self.dir_id = dir_id

    def get_name(self):
        """Overrides"""
        return self.name
