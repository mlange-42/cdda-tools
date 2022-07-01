from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def exec(self, arg):
        pass
