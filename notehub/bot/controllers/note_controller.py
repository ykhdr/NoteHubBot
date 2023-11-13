from bot.models.note import Note
from bot.repositories.cur_user_dir_repository import CurrentUserDirectoryRepository
from bot.repositories.dir_repository import DirectoryRepository
from bot.repositories.note_repository import NoteRepository


class NoteController:
    def __init__(self):
        self.__note_repository = NoteRepository()
        self.__current_user_directory_repository = CurrentUserDirectoryRepository()

    def get_notes_in_directory(self, chat_id, dir_id) -> [Note]:
        return self.__note_repository.get_notes_in_directory(chat_id, dir_id)

    def create_note(self, chat_id, dir_id, name, content):
        note = Note(name, content, chat_id, dir_id)
        return self.__note_repository.add_note(note)

    def is_node_in_cur_directory_exists(self, chat_id, note_name):
        cur_dir = self.__current_user_directory_repository.get_current_directory(chat_id)
        return self.__note_repository.is_note_in_directory_exists(chat_id, cur_dir.dir_id, note_name)
