from bot.database.database import Database
from bot.models.user import User


class UserRepository:
    def __init__(self):
        self.__db = Database()

    def add_user(self, user: User):
        session = self.__db.get_session()
        if self.get_user(user.chat_id) is not None:
            return

        session.add(user)
        session.commit()
        print(f'User {user.chat_id} has been created')
        session.close()

    def get_user(self, id):
        session = self.__db.get_session()
        user = session.query(User).get(id)
        session.close()

        return user
