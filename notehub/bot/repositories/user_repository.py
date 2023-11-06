from bot.database.database import Database
from bot.models.user import User


class UserRepository:
    def __init__(self):
        self.__db = Database()

    def add_user(self, user: User):
        session = self.__db.get_session()
        session.add(user)
        session.commit()
        session.close()

    def get_user(self, user_id):
        session = self.__db.get_session()
        user = session.query(User).get(user_id)
        session.close()

        return user
