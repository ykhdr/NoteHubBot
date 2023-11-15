from bot.models.entities.user import User
from bot.repositories.user_repository import UserRepository


class AuthController:
    def __init__(self):
        self.__user_repository = UserRepository()

    def create_user(self, chat_id: int, user_id):
        user = User(chat_id, user_id)
        self.__user_repository.add_user(user)