import abc
from abc import ABC


class Handler(ABC):

    @abc.abstractmethod
    def setup_handler(self):
        pass
