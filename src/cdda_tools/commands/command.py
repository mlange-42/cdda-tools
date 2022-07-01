from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def add_subcommand(self, subparsers):
        pass

    @abstractmethod
    def exec(self, arg):
        pass
