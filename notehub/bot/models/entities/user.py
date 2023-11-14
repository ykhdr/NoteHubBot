from sqlalchemy import Column, BigInteger

from bot.models.entities.entity import Entity


class User(Entity.get_entity_class_instance()):
    __tablename__ = 'users'

    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)
    user_id = Column(BigInteger, nullable=False)

    def __init__(self, chat_id, user_id):
        self.chat_id = chat_id
        self.user_id = chat_id

    def get_id(self):
        return self.chat_id
