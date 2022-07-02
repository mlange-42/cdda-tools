import os
from os import path
import argparse

from . import Command, util
from .. import json


class FilterNotes(Command):
    def add_subcommand(self, subparsers):
        parser_copy_player = subparsers.add_parser(
            "filter-notes",
            help="Filter overmap notes by symbol or text.",
            description="Filter overmap notes by symbol or text.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_copy_player.add_argument(
            "--world",
            "-w",
            type=str,
            required=True,
            help="the game world to copy from",
        )
        parser_copy_player.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to modify notes for, optional if only one player in world",
        )

    def exec(self, arg):
        pass
