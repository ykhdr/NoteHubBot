from abc import abstractmethod, ABC

from bot.models import Entity


class Storage:
    @abstractmethod
    def get_name(self):
        pass
