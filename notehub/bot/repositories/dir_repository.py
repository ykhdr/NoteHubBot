from bot.database.database import Database
from bot.models.directory import Directory


class DirectoryRepository:
    def __init__(self):
        self.__db = Database()

    def add_directory(self, dir: Directory):
        session = self.__db.get_session()

        if session.query(Directory).filter(Directory.name == dir.name,
                                           Directory.chat_id == dir.chat_id,
                                           Directory.parent_dir_id == dir.parent_dir_id).all():
            session.close()
            return None

        session.add(dir)
        print(f'User {dir.chat_id} has created a directory : {dir.name}')
        session.commit()

        session.refresh(dir)
        session.close()
        return dir

    def get_child_directories(self, user_id, parent_dir_id):
        session = self.__db.get_session()
        dirs = session.query(Directory).filter(Directory.chat_id == user_id,
                                               Directory.parent_dir_id == parent_dir_id).all()
        session.close()

        return dirs

    def get_directory(self, dir_id):
        session = self.__db.get_session()
        dir = session.query(Directory).filter(Directory.id == dir_id).one()
        session.close()

        return dir
