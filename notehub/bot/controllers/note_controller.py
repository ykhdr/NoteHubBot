from bot.models.entities.note import Note
from bot.repositories.cur_user_dir_repository import CurrentUserDirectoryRepository
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

    def get_note(self, note_id):
        return self.__note_repository.get_note(note_id)

    def delete_note(self, note_id):
        return self.__note_repository.remove_note(note_id)

    def rename_note(self, note_id, new_name):
        return self.__note_repository.rename_note(note_id, new_name)

    def update_note_content(self, note_id, new_content):
        return self.__note_repository.update_content(note_id, new_content)

    def get_user_notes_like(self, user_id, text):
        return self.__note_repository.get_user_notes_like(user_id, text)
