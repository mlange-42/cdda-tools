import argparse
from os import path

from .. import json
from . import Command, util


class CopyVehicle(Command):
    """Copy a vehicle between worlds"""

    def add_subcommand(self, subparsers):
        parser_copy_player = subparsers.add_parser(
            "copy-vehicle",
            help="Copies a vehicle from one world to another.",
            description="Copies a vehicle from one world to another\n\n"
            "  1. Give the vehicle to be copied a unique name\n"
            "  2. Debug a vehicle into the new world, or find one; it will be replaced by the source vehicle\n"
            "  3. Give the vehicle in the new world a unique name\n"
            "  2. Use this command with the names of the old and new worlds, and the old and new vehicles:\n"
            "     cdda_tools copy-player -w OldWorld -v OldVehicle -w2 NewWorld -v2 NewVehicle",
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
            "--vehicle",
            "-v",
            type=str,
            required=True,
            help="the (unique!) name of the vehicle to copy from",
        )

        parser_copy_player.add_argument(
            "--world2",
            "-w2",
            type=str,
            required=True,
            help="the game world to copy to",
        )
        parser_copy_player.add_argument(
            "--vehicle2",
            "-v2",
            type=str,
            required=True,
            help="the (unique!) name of the vehicle to copy to",
        )

    def exec(self, arg):
        world_dir_1 = util.get_world_path(arg.dir, arg.world)
        world_dir_2 = util.get_world_path(arg.dir, arg.world2)

        source_path = path.join(world_dir_1, util.MAPS_DIR)
        source_maps = util.find_files_with_text(source_path, arg.vehicle)

        target_path = path.join(world_dir_2, util.MAPS_DIR)
        target_maps = util.find_files_with_text(target_path, arg.vehicle2)

        if len(source_maps) == 0:
            print("Could not find source vehicle '{}'".format(arg.vehicle))
            exit(1)
        if len(source_maps) > 1:
            print(
                "Found multiple files for source vehicle name '{}'.\nPlease rename the vehicle to something unique.".format(
                    arg.vehicle
                )
            )
            exit(1)

        if len(target_maps) == 0:
            print("Could not find target vehicle '{}'".format(arg.vehicle2))
            exit(1)
        if len(target_maps) > 1:
            print(
                "Found multiple files for target vehicle name '{}'.\nPlease rename the vehicle to something unique.".format(
                    arg.vehicle2
                )
            )
            exit(1)

        print(
            "Copying vehicle {} ({}) -> {} ({})".format(
                arg.vehicle, world_dir_1, arg.vehicle2, world_dir_2
            )
        )

        sources = json.read_json(source_maps[0])
        targets = json.read_json(target_maps[0])

        source_vehicle = None
        target_vehicle = None

        for source in sources:
            for veh in source["vehicles"]:
                if veh["name"] == arg.vehicle:
                    if source_vehicle is not None:
                        print(
                            "Found multiple vehicles for source name '{}'.\nPlease rename the vehicle to something unique.".format(
                                arg.vehicle
                            )
                        )
                        exit(1)
                    else:
                        source_vehicle = veh

        for target in targets:
            for veh in target["vehicles"]:
                if veh["name"] == arg.vehicle2:
                    if target_vehicle is not None:
                        print(
                            "Found multiple vehicles for target_vehicle name '{}'.\nPlease rename the vehicle to something unique.".format(
                                arg.vehicle
                            )
                        )
                        exit(1)
                    else:
                        target_vehicle = veh

        if source_vehicle is None:
            print("Could not find source vehicle '{}'".format(arg.vehicle))
            exit(1)
        if target_vehicle is None:
            print("Could not find target vehicle '{}'".format(arg.vehicle))
            exit(1)

        target_vehicle["parts"] = source_vehicle["parts"]

        json.write_json(targets, target_maps[0])

        print(
            "Successfully copied vehicle {} ({}) -> {} ({})".format(
                arg.vehicle, world_dir_1, arg.vehicle2, world_dir_2
            )
        )
