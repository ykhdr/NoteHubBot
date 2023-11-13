from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.database import DB_URL
from bot.models import Entity


class Database:
    def __init__(self):
        engine = create_engine(DB_URL)
        self.__session = sessionmaker(bind=engine)
        Entity.metadata.create_all(engine)

    def get_session(self):
        return self.__session()
