from abc import abstractmethod


class Storage:
    @abstractmethod
    def get_name(self):
        pass
