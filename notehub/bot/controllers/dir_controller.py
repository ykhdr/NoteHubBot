from __future__ import annotations

from bot.models.entities.cur_user_dir import CurrentUserDirectory
from bot.models.entities.directory import Directory
from bot.repositories.cur_user_dir_repository import CurrentUserDirectoryRepository
from bot.repositories.dir_repository import DirectoryRepository
from bot.repositories.user_repository import UserRepository


class DirectoryController:
    def __init__(self):
        self.__directory_repository = DirectoryRepository()
        self.__user_repository = UserRepository()
        self.__current_user_directory_repository = CurrentUserDirectoryRepository()

    def create_root(self, chat_id):
        root = Directory('/', chat_id, None)
        return self.__directory_repository.add_root(root)

    def create_directory(self, name, chat_id, parent_dir_id):
        directory = Directory(name, chat_id, parent_dir_id)
        return self.__directory_repository.add_directory(directory)

    def get_child_directories(self, chat_id, parent_dir_id):
        return self.__directory_repository.get_child_directories(chat_id, parent_dir_id)

    def get_directory(self, dir_id) -> Directory:
        return self.__directory_repository.get_directory(dir_id)

    def delete_directory(self, dir: Directory):
        return self.__directory_repository.remove_directory(dir)

    def create_user_current_directory(self, chat_id, dir_id):
        cur_user_dir = CurrentUserDirectory(chat_id, dir_id)

        self.__current_user_directory_repository.add_current_user_directory(cur_user_dir)

    def get_current_directory(self, chat_id) -> Directory | None:
        cur_user_dir = self.__current_user_directory_repository.get_current_directory(chat_id)
        if cur_user_dir is None:
            return None

        return self.__directory_repository.get_directory(cur_user_dir.dir_id)

    def change_current_directory(self, chat_id, cur_dir_id):
        self.__current_user_directory_repository.update_user_current_directory(chat_id, cur_dir_id)

    def get_root_directory(self, chat_id):
        return self.__directory_repository.get_root_directory(chat_id)

    def is_directory_in_cur_parent_exists(self, chat_id, dir_name):
        cur_dir = self.__current_user_directory_repository.get_current_directory(chat_id)
        return self.__directory_repository.is_directory_in_parent_exists(chat_id, cur_dir.dir_id, dir_name)

    def rename_directory(self, dir_id, new_name):
        return self.__directory_repository.rename_directory(dir_id, new_name)
