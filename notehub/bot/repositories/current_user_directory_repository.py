import psycopg2.errors
from bot.database.database import Database
from bot.models.directory import Directory
from bot.models.user import User
from bot.models.current_user_directory import CurrentUserDirectory


class CurrentUserDirectoryRepository:

    def __init__(self):
        self.__db = Database()

    def add_current_user_directory(self, current_user_directory: CurrentUserDirectory):
        session = self.__db.get_session()

        if session.query(CurrentUserDirectory).filter(CurrentUserDirectory.chat_id == current_user_directory.chat_id). \
                all():
            session.close()
            print(f'Current directory {current_user_directory.dir_id} is already exists table for user '
                  f'{current_user_directory.chat_id}')
            return None

        session.add(current_user_directory)
        session.commit()
        print(f'New current user directory with chat id: {current_user_directory.chat_id}')
        session.close()

    def update_user_current_directory(self, user: User, directory: Directory):
        session = self.__db.get_session().query().update()

        session.query(CurrentUserDirectory).filter(CurrentUserDirectory.chat_id == user.chat_id). \
            update({CurrentUserDirectory.dir_id: directory.id})

        session.commit()
        session.close()
