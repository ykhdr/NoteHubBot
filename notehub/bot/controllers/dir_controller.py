from bot.models.directory import Directory
from bot.repositories.dir_repository import DirectoryRepository
from bot.repositories.user_repository import UserRepository


class DirectoryController:
    def __init__(self):
        self.__directory_repository = DirectoryRepository()
        self.__user_repository = UserRepository()

    def create_directory(self, name, user_id, parent_dir_id):
        directory = Directory(name, user_id, parent_dir_id)
        return self.__directory_repository.add_directory(directory)

    def get_child_directories(self, user_id, parent_dir_id):
        return self.__directory_repository.get_child_directories(user_id, parent_dir_id)

    def get_directory(self, dir_id):
        return self.__directory_repository.get_directory(dir_id)
