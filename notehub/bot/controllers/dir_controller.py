from bot.models.directory import Directory
from bot.models.current_user_directory import CurrentUserDirectory
from bot.repositories.current_user_directory_repository import CurrentUserDirectoryRepository
from bot.repositories.dir_repository import DirectoryRepository
from bot.repositories.user_repository import UserRepository


class DirectoryController:
    def __init__(self):
        self.__directory_repository = DirectoryRepository()
        self.__user_repository = UserRepository()
        self.__current_user_directory_repository = CurrentUserDirectoryRepository()

    def create_directory(self, name, chat_id, parent_dir_id):
        directory = Directory(name, chat_id, parent_dir_id)
        return self.__directory_repository.add_directory(directory)

    def get_child_directories(self, chat_id, parent_dir_id):
        return self.__directory_repository.get_child_directories(chat_id, parent_dir_id)

    def get_directory(self, dir_id) -> Directory:
        return self.__directory_repository.get_directory(dir_id)

    def add_user_current_directory(self, chat_id, dir_id):
        cur_user_dir = CurrentUserDirectory(chat_id, dir_id)

        # TODO возможно добавить возвращаемое значение
        self.__current_user_directory_repository.add_current_user_directory(cur_user_dir)
