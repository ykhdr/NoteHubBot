import sys

import psycopg2.errors
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import subqueryload

from bot.database.database import Database
from bot.models.directory import Directory


class DirectoryRepository:
    def __init__(self):
        self.__db = Database()

    def add_directory(self, dir: Directory):
        session = self.__db.get_session()

        if self.is_directory_in_parent_exists(dir.chat_id,dir.parent_dir_id, dir.name):
            session.close()
            print(f'Directory {dir.name} is already exists in current dir for user {dir.chat_id}', file=sys.stderr)
            return None

        session.add(dir)
        session.commit()
        session.refresh(dir)
        print(f'User {dir.chat_id} has created a directory : {dir.name}')
        session.close()
        return dir

    def get_child_directories(self, user_id, parent_dir_id):
        session = self.__db.get_session()
        dirs = (session.query(Directory).filter(Directory.chat_id == user_id,
                                                Directory.parent_dir_id == parent_dir_id).options(
            subqueryload(Directory.parent_dir), subqueryload(Directory.user)).all())

        session.close()

        return dirs

    def get_directory(self, dir_id):
        session = self.__db.get_session()
        dir = session.query(Directory).filter(Directory.id == dir_id).options(
            subqueryload(Directory.parent_dir)
        ).one()

        session.close()

        return dir

    def remove_directory(self, dir):
        session = self.__db.get_session()
        session.query(Directory).filter(Directory.id == dir.id).delete()
        session.commit()
        print(f'Directory {dir.id} has deleted')
        session.close()

    def get_root_directory(self, chat_id):
        session = self.__db.get_session()

        dir = session.query(Directory).filter(Directory.chat_id == chat_id, Directory.parent_dir_id == None).options(
            subqueryload(Directory.parent_dir), subqueryload(Directory.user)
        ).one()
        session.close()

        return dir

    def is_directory_in_parent_exists(self, chat_id, parent_dir_id, dir_name) -> bool:
        session = self.__db.get_session()

        dir = session.query(Directory).filter(
            Directory.chat_id == chat_id,
            Directory.parent_dir_id == parent_dir_id,
            Directory.name == dir_name
        ).first()

        session.close()

        return dir is not None
