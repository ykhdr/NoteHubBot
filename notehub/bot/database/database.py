import os

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from bot.models.entities.entity import Entity


class Database:
    __DB_URL = os.getenv('DB_URL')

    def __init__(self):
        sqlalchemy.pool_recycle = 299
        sqlalchemy.pool_timeout = 20
        engine = create_engine(Database.__DB_URL)
        self.__session = sessionmaker(bind=engine)
        Entity.get_entity_class_instance().metadata.create_all(engine)

    def get_session(self):
        return self.__session()
