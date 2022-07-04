"""Read game data."""
import argparse
import sys

from .. import game
from . import Command


class ReadData(Command):
    """Read game data."""

    def add_subcommand(self, subparsers):
        _parser = subparsers.add_parser(
            "read-data",
            help="Read game data.",
            description="Read game data.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

    def exec(self, arg):
        data = game.read_game_data(arg.dir)
