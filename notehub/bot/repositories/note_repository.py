from bot.database.database import Database


class NoteRepository:
    def __init__(self):
        self.__db = Database()
