from sqlalchemy.orm import subqueryload

from bot.database.database import Database
from bot.models.note import Note


class NoteRepository:
    def __init__(self):
        self.__db = Database()

    def get_notes_in_directory(self, chat_id, dir_id):
        session = self.__db.get_session()

        notes = (session.query(Note).filter(Note.chat_id == chat_id, Note.dir_id == dir_id)
                 .options(subqueryload(Note.dir), subqueryload(Note.user)).all())

        session.close()
        return notes
