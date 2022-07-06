"""Create a mod file from an in-game vehicle."""
import argparse
import json
from os import path

from .. import json_utils
from . import Command, util

TANKS = {"tank", "tank_medium", "tank_small", "external_tank"}


class VehicleMod(Command):
    """Create a mod file from an in-game vehicle."""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "vehicle-mod",
            help="Create a mod file from an in-game vehicle.",
            description="Create a mod file from an in-game vehicle.\n\n"
            "  1. Give the vehicle a unique name in-game\n"
            "  2. Use this command\n\n"
            "Examples:\n\n"
            '  cdda_tools vehicle-mod -w MyWorld -v "My Death Mobile" --id death_mobile '
            "> my_death_mobile.json",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world to search for the vehicle")

        util.add_vehicle_option(
            parser, "the (unique!) name of the in-game vehicle to use"
        )

        parser.add_argument(
            "--id",
            "-i",
            type=str,
            required=True,
            help="the new vehicle's id string",
        )
        parser.add_argument(
            "--no-items",
            action="store_true",
            help="do not add items to the mod vehicle",
        )

    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        source_path = path.join(world_dir, util.MAPS_DIR)
        source_maps = util.find_files_with_text(source_path, arg.vehicle)

        util.check_is_single_vehicle_source(source_maps, arg.vehicle)

        source_map = source_maps[0]
        sources = json_utils.read_json(source_map)
        source_vehicle = None

        for source in sources:
            for veh in source["vehicles"]:
                if veh["name"] == arg.vehicle:
                    if source_vehicle is not None:
                        raise ValueError(
                            "Found multiple vehicles for name '{}'.\n"
                            "Please rename the vehicle to something unique.".format(
                                arg.vehicle
                            )
                        )

                    source_vehicle = veh

        if source_vehicle is None:
            raise ValueError("Could not find vehicle '{}'".format(arg.vehicle))

        mod_json = vehicle_to_mod(source_vehicle, arg.id, arg.no_items)
        yield json.dumps(mod_json, indent=4)


def vehicle_to_mod(vehicle, vehicle_id, no_items):
    """Converts a vehicle to a vehicle definition for mods"""
    # pylint: disable=too-many-locals

    parts = []
    items = []

    # pylint: disable=too-many-nested-blocks
    for part in vehicle["parts"]:
        part_id = part["id"]
        if "variant" in part:
            part_id = "{}_{}".format(part_id, part["variant"])
        part_def = {"x": part["mount_dx"], "y": part["mount_dy"], "part": part_id}
        if part_id in TANKS:
            base = part["base"]
            if "contents" in base:
                for cont in base["contents"]["contents"]:
                    fuel_type = None
                    for content in cont["contents"]:
                        if "typeid" in content:
                            fuel_type = content["typeid"]
                    if fuel_type is not None:
                        part_def["fuel"] = fuel_type

        if not no_items:
            for item in part["items"]:
                count = 1
                if isinstance(item, list):
                    count = item[1]
                    item = item[0]

                item_def = {
                    "x": part["mount_dx"],
                    "y": part["mount_dy"],
                    "chance": 100,
                    "items": item["typeid"],
                }

                for _ in range(count):
                    items.append(item_def)

        parts.append(part_def)

    parts.sort(key=lambda p: abs(p["x"]) + abs(p["y"]))

    obj = {
        "id": vehicle_id,
        "type": "vehicle",
        "name": vehicle["name"],
        "blueprint": [["+"]],
        "parts": parts,
        "items": items,
    }

    return obj
