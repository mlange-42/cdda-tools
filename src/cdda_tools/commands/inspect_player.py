"""Inspect the player"""
import argparse
import json

from .. import json_utils
from . import Command, util


class InspectPlayer(Command):
    """Inspect the player"""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "player",
            help="Inspect the player.",
            description="Inspect the player.\n\n"
            "Example:\n\n"
            "  cdda_tools player ...",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world")

        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to inspect, optional if only one player in world",
        )

    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        save, _, _player_name = util.get_save_path(world_dir, arg.player)

        source = json_utils.read_json(save)
        player = source["player"]

        print(json.dumps(player, indent=4))
