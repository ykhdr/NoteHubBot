from bot.database.database import Database


class DirectoryRepository:
    def __init__(self):
        self.__db = Database()