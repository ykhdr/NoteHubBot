import psycopg2.errors
from sqlalchemy.orm import subqueryload

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

    def update_user_current_directory(self, chat_id, dir_id):
        session = self.__db.get_session()

        session.query(CurrentUserDirectory).filter(CurrentUserDirectory.chat_id == chat_id). \
            update({CurrentUserDirectory.dir_id: dir_id}, synchronize_session=False)

        session.commit()
        session.close()

    def get_current_directory(self, chat_id):
        session = self.__db.get_session()

        cur_user_dir = session.query(CurrentUserDirectory).filter(CurrentUserDirectory.chat_id == chat_id).options(
            subqueryload(CurrentUserDirectory.dir).subqueryload(Directory.parent_dir)
    ).one()
        session.refresh(cur_user_dir)
        session.close()

        return cur_user_dir
