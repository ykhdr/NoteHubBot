from sqlalchemy.orm import declarative_base


class Entity:
    __class_instance = declarative_base()

    @staticmethod
    def get_entity_class_instance():
        return Entity.__class_instance
