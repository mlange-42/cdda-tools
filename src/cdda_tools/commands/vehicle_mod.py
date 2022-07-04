import argparse
import json
from os import path

from .. import json as cjson
from . import Command, util

TANKS = set(["tank", "tank_medium", "tank_small", "external_tank"])


class VehicleMod(Command):
    """Create a mod file from an in-game vehicle."""

    def add_subcommand(self, subparsers):
        parser_copy_player = subparsers.add_parser(
            "vehicle-mod",
            help="Creates a mod file from an in-game vehicle.",
            description="Creates a mod file from an in-game vehicle.\n\n"
            "  1. Give the vehicle a unique name in-game\n"
            "  2. Use this command",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_copy_player.add_argument(
            "--world",
            "-w",
            type=str,
            required=True,
            help="the game world to search for the vehicle",
        )
        parser_copy_player.add_argument(
            "--vehicle",
            "-v",
            type=str,
            required=True,
            help="the (unique!) name of the in-game vehicle to use",
        )
        parser_copy_player.add_argument(
            "--id",
            "-i",
            type=str,
            required=True,
            help="the new vehicle's id string",
        )
        parser_copy_player.add_argument(
            "--no-items",
            action="store_true",
            help="do not add items to the mod vehicle",
        )

    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        source_path = path.join(world_dir, util.MAPS_DIR)
        source_maps = util.find_files_with_text(source_path, arg.vehicle)

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

        source_map = source_maps[0]
        sources = cjson.read_json(source_map)
        source_vehicle = None

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

        if source_vehicle is None:
            print("Could not find source vehicle '{}'".format(arg.vehicle))
            exit(1)

        mod_json = vehicle_to_mod(source_vehicle, arg.id, arg.no_items)
        print(json.dumps(mod_json, indent=4))


def vehicle_to_mod(vehicle, id, no_items):
    parts = []
    items = []

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
                    for c in cont["contents"]:
                        if "typeid" in c:
                            fuel_type = c["typeid"]
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

                for i in range(count):
                    items.append(item_def)

        parts.append(part_def)

    parts.sort(key=lambda p: abs(p["x"]) + abs(p["y"]))

    obj = {
        "id": id,
        "type": "vehicle",
        "name": vehicle["name"],
        "blueprint": [["+"]],
        "parts": parts,
        "items": items,
    }

    return obj
