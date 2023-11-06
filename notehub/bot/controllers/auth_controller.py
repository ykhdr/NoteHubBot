from bot.repositories.user_repository import UserRepository


class AuthController:
    def __init__(self):
        self.__user_repository = UserRepository()

    def create_user(self):
        self.__user_repository
