from sqlalchemy import Column, BigInteger

from bot.models.entities.entity import Entity


class User(Entity.getEntityClassInstance()):
    __tablename__ = 'users'

    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def get_id(self):
        return self.chat_id
