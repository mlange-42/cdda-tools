from os import path

from . import Command, util
from .. import json

PROPERTIES = [
    "pain",
    "effects",
    "body",
    "weapon",
    "str_cur",
    "str_max",
    "dex_cur",
    "dex_max",
    "int_cur",
    "int_max",
    "per_cur",
    "per_max",
    "str_bonus",
    "dex_bonus",
    "per_bonus",
    "int_bonus",
    "base_age",
    "base_height",
    "blood_type",
    "blood_rh_factor",
    "avg_nat_bpm",
    "custom_profession",
    "healthy",
    "healthy_mod",
    "health_tally",
    "thirst",
    "hunger",
    "fatigue",
    "cardio_acc",
    "sleep_deprivation",
    "stored_calories",
    "radiation",
    "stamina",
    "vitamin_levels",
    "type_of_scent",
    "focus_pool",
    "kill_xp",
    "spent_upgrade_points",
    "traits",
    "mutations",
    "martial_arts_data",
    "my_bionics",
    "skills",
    "proficiencies",
    "power_level",
    "max_power_level_modifier",
    "stomach",
    "guts",
    "slow_rad",
    "scent",
    "male",
    "worn",
    "inv",
    "profession",
    "learned_recipes",
    "items_identified",
    "snippets_read",
    "assigned_invlet",
    "invcache",
    "calorie_diary"
]

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

        for prop in PROPERTIES:
            target["player"][prop] = source["player"][prop]

        json.write_json(target, save_2)

        print("Successfully copied {} ({}) -> {} ({})".format(player_1, world_dir_1, player_2, world_dir_2))
