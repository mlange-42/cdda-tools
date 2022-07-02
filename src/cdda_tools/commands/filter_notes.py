from os import path
import argparse
import glob

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
        world_dir = util.get_world_path(arg.dir, arg.world)
        save, save_name, player = util.get_save_path(world_dir, arg.player)

        print(
            "Filtering notes for {} ({})".format(
                player, world_dir,
            )
        )

        seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))

        for file in seen_files:
            content = json.read_json(file)
            notes = content["notes"]
            for i in range(len(notes)):
                notes[i] = list(filter(lambda n: n[2].startswith("."), notes[i]))

