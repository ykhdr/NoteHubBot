import sys

from sqlalchemy.orm import subqueryload

from bot.database.database import Database
from bot.models.entities.directory import Directory
from bot.models.entities.note import Note
from bot.models.entities.user import User


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

    def get_note(self, note_id):
        session = self.__db.get_session()

        note = session.get(Note, note_id)

        session.close()

        return note

    def remove_note(self, note_id):
        session = self.__db.get_session()

        session.query(Note).filter(Note.id == note_id).delete()

        session.commit()
        session.close()

        print(f'Note {note_id} has deleted')

    def rename_note(self, note_id, new_name):
        session = self.__db.get_session()

        session.query(Note).filter(Note.id == note_id).update({Note.name: new_name}, synchronize_session=False)

        session.commit()
        session.close()
        print(f'Note {note_id} has renamed to {new_name}')

    def update_content(self, note_id, new_content):
        session = self.__db.get_session()

        session.query(Note).filter(Note.id == note_id).update({Note.content: new_content}, synchronize_session=False)

        session.commit()
        session.close()

        print(f'Note {note_id} has changed content')

    def get_user_notes_like(self, user_id, text):
        session = self.__db.get_session()

        notes = (session.query(Note).join(User).filter(User.user_id == user_id)
                 .filter(Note.name.startswith(text))
                 .options(subqueryload(Note.dir).joinedload(Directory.parent_dir), subqueryload(Note.user))
                 .all())

        session.close()

        return notes
