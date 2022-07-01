from os import path

from . import Command, util
from .. import json


class CopyPlayer(Command):

    def add_subcommand(self, subparsers):
        parser_copy_player = subparsers.add_parser("copy-player", help="copy-player help")

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
            help="the player to copy from, optional if only one player in world",
        )

        parser_copy_player.add_argument(
            "--world2",
            "-w2",
            type=str,
            required=True,
            help="the game world to copy to",
        )
        parser_copy_player.add_argument(
            "--player2",
            "-p2",
            type=str,
            help="the player to copy to, optional if only one player in world",
        )

    def exec(self, arg):
        world_dir_1 = util.get_world_path(arg.dir, arg.world)
        save_1, player_1 = util.get_save_path(world_dir_1, arg.player)

        world_dir_2 = util.get_world_path(arg.dir, arg.world2)
        save_2, player_2 = util.get_save_path(world_dir_2, arg.player2)

        print("Copying {} ({}) -> {} ({})".format(player_1, world_dir_1, player_2, world_dir_2))

        source = json.read_json(save_1, skip_lines=1)
        target = json.read_json(save_2, skip_lines=1)

