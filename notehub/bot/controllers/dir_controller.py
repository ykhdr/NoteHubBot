from bot.repositories.dir_repository import DirectoryRepository
from bot.repositories.user_repository import UserRepository


class DirectoryController:
    def __init__(self):
        self.__directory_repository = DirectoryRepository()
        self.__user_repository = UserRepository()
