import os
from os import path
import argparse
import glob

from . import Command, util
from .. import json


class Find(Command):
    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "find",
            help="Find terrain or items.",
            description="Find terrain or items.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser.add_argument(
            "--world",
            "-w",
            type=str,
            required=True,
            help="the game world serch in",
        )
        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to rearch for",
        )
        parser.add_argument(
            "--terrain",
            "-t",
            type=str,
            nargs="+",
            help="search terrain by glob pattern(s)",
        )

    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        save, save_name, player = util.get_save_path(world_dir, arg.player)

        print(
            "Searching for {} ({})".format(
                player,
                world_dir,
            )
        )

        seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))
        seen_coords = [list(map(int, f.split(".")[-2:])) for f in seen_files]
        files_overmap = [
            path.join(world_dir, "o.{}.{}".format(*xy)) for xy in seen_coords
        ]
