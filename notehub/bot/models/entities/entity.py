from sqlalchemy.orm import declarative_base


class Entity:
    __class_instance = declarative_base()

    @staticmethod
    def getEntityClassInstance():
        return Entity.__class_instance
