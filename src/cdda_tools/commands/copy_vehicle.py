"""Copy a vehicle between worlds"""
import argparse
from os import path

from .. import json_utils as json
from . import Command, util


class CopyVehicle(Command):
    """Copy a vehicle between worlds"""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "copy-vehicle",
            help="Copy a vehicle from one world to another.",
            description="Copy a vehicle from one world to another\n\n"
            "  1. Give the vehicle to be copied a unique name\n"
            "  2. Debug a vehicle into the new world, or find one; "
            "it will be replaced by the source vehicle\n"
            "  3. Give the vehicle in the new world a unique name\n"
            "  2. Use this command with the names of the old and new worlds, "
            "and the old and new vehicles\n\n"
            "Example:\n\n"
            "  cdda_tools copy-vehicle -w OldWorld -v OldVehicle -w2 NewWorld -v2 NewVehicle",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world to copy from")

        util.add_vehicle_option(
            parser, "the (unique!) name of the vehicle to copy from"
        )

        util.add_world2_option(parser, "the game world to copy to")

        parser.add_argument(
            "--vehicle2",
            "-v2",
            type=str,
            required=True,
            help="the (unique!) name of the vehicle to copy to",
        )

        util.add_dry_run_options(parser)

    def exec(self, arg):
        world_dir_1 = util.get_world_path(arg.dir, arg.world)
        world_dir_2 = util.get_world_path(arg.dir, arg.world2)

        source_path = path.join(world_dir_1, util.MAPS_DIR)
        source_maps = util.find_files_with_text(source_path, arg.vehicle)

        target_path = path.join(world_dir_2, util.MAPS_DIR)
        target_maps = util.find_files_with_text(target_path, arg.vehicle2)

        util.check_is_single_vehicle_source(source_maps, arg.vehicle)
        util.check_is_single_vehicle_source(target_maps, arg.vehicle2)

        print(
            "Copying vehicle {} ({}) -> {} ({})".format(
                arg.vehicle, world_dir_1, arg.vehicle2, world_dir_2
            )
        )

        sources = json.read_json(source_maps[0])
        targets = json.read_json(target_maps[0])

        source_vehicle = _find_vehicle(sources, arg.vehicle)
        target_vehicle = _find_vehicle(targets, arg.vehicle2)

        if source_vehicle is None:
            raise ValueError("Could not find source vehicle '{}'".format(arg.vehicle))
        if target_vehicle is None:
            raise ValueError("Could not find target vehicle '{}'".format(arg.vehicle2))

        target_vehicle["parts"] = source_vehicle["parts"]

        if not arg.dry:
            json.write_json(targets, target_maps[0])

        print(
            "Successfully copied vehicle {} ({}) -> {} ({})".format(
                arg.vehicle, world_dir_1, arg.vehicle2, world_dir_2
            )
        )


def _find_vehicle(sources, name):
    vehicle = None
    for source in sources:
        for veh in source["vehicles"]:
            if veh["name"] == name:
                if vehicle is not None:
                    raise ValueError(
                        "Found multiple vehicles for source name '{}'.\n"
                        "Please rename the vehicle to something unique.".format(name)
                    )

                vehicle = veh

    return vehicle
