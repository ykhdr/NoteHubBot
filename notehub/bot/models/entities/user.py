from sqlalchemy import Column, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship

from bot.models.entities.entity import Entity


class User(Entity.get_entity_class_instance()):
    __tablename__ = 'users'
    __table_args__ = (UniqueConstraint('user_id', name='uq_user_id'),)

    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)
    user_id = Column(BigInteger, nullable=False)

    directories = relationship('Directory', back_populates='user',overlaps="directories")  # Добавляем обратное отношение
    notes = relationship('Note', back_populates='user')

    def __init__(self, chat_id, user_id):
        self.chat_id = chat_id
        self.user_id = user_id
