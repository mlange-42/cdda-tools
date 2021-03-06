"""Copy the player between worlds"""
import argparse

from .. import json_utils as json
from . import Command, util

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
    "calorie_diary",
]


class CopyPlayer(Command):
    """Copy the player between worlds"""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "copy-player",
            help="Copy a player from one world to another.",
            description="Copy a vehicle from one world to another\n\n"
            "  1. Create a player in the new world; it will be 'replaced' by the source player\n"
            "  2. Use this command with the names of the old and new worlds, "
            "and the old and new players\n\n"
            "Example:\n\n"
            "  cdda_tools copy-player -w OldWorld -p OldPlayer -w2 NewWorld -p2 NewPlayer",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world to copy from")

        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to copy from, optional if only one player in world",
        )

        util.add_world2_option(parser, "the game world to copy to")

        parser.add_argument(
            "--player2",
            "-p2",
            type=str,
            help="the player to copy to, optional if only one player in world",
        )

        util.add_dry_run_options(parser)

    def exec(self, arg):
        world_dir_1 = util.get_world_path(arg.dir, arg.world)
        save_1, _, player_1 = util.get_save_path(world_dir_1, arg.player)

        world_dir_2 = util.get_world_path(arg.dir, arg.world2)
        save_2, _, player_2 = util.get_save_path(world_dir_2, arg.player2)

        yield "Copying player {} ({}) -> {} ({})".format(
            player_1, world_dir_1, player_2, world_dir_2
        )

        source = json.read_json(save_1)
        target = json.read_json(save_2)

        for prop in PROPERTIES:
            if prop in source["player"]:
                target["player"][prop] = source["player"][prop]
            elif prop in target["player"]:
                del target["player"]
                yield (
                    "Warning: missing property '{}' in source player! "
                    "Removing it from target player."
                ).format(prop)

        if arg.dry:
            yield "Skip writing back to player file (--dry)"
        else:
            yield "Writing back to player file"
            json.write_json(target, save_2)

        yield "Successfully copied player {} ({}) -> {} ({})".format(
            player_1, world_dir_1, player_2, world_dir_2
        )
