from bot.models.note import Note
from bot.repositories.note_repository import NoteRepository


class NoteController:
    def __init__(self):
        self.__note_repository = NoteRepository()

    def get_notes_in_directory(self, chat_id, dir_id) -> [Note]:
        return self.__note_repository.get_notes_in_directory(chat_id, dir_id)
