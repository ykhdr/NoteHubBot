from sqlalchemy.orm import subqueryload

from bot.database.database import Database
from bot.models.note import Note


class NoteRepository:
    def __init__(self):
        self.__db = Database()

    def get_notes_in_directory(self, chat_id, dir_id) -> [Note]:
        session = self.__db.get_session()

        notes = (session.query(Note).filter(Note.chat_id == chat_id, Note.dir_id == dir_id)
                 .options(subqueryload(Note.dir), subqueryload(Note.user)).all())

        session.close()
        return notes

    def add_note(self, note: Note):
        session = self.__db.get_session()

        print(f'User {note.chat_id} has created a note : {note.name}')

        if self.is_note_in_directory_exists(note.chat_id, note.dir_id, note.get_name()):
            session.close()
            print(f'Note {note.get_name()} is already exists in current dir for user {note.chat_id}', file=sys.stderr)
            return None

        session.add(note)
        session.commit()
        session.refresh(note)
        print(f'User {note.chat_id} has created a note : {note.name}')
        session.close()

        return note

    def is_note_in_directory_exists(self, chat_id, dir_id, note_name) -> bool:
        session = self.__db.get_session()

        note = session.query(Note).filter(
            Note.chat_id == chat_id,
            Note.dir_id == dir_id,
            Note.name == note_name
        ).first()

        session.close()

        return note is not None
