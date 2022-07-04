from abc import ABC, abstractmethod


class Command(ABC):
    """Base class for CLI commands"""

    @abstractmethod
    def add_subcommand(self, subparsers):
        """Fill the parser with sub-parser and arguments"""
        pass

    @abstractmethod
    def exec(self, arg):
        """Execute the command"""
        pass
