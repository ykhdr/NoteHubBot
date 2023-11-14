import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


class Database:
    __DB_URL = os.getenv('DB_URL')

    def __init__(self):
        engine = create_engine(Database.__DB_URL)
        self.__session = sessionmaker(bind=engine)
        declarative_base().metadata.create_all(engine)

    def get_session(self):
        return self.__session()
