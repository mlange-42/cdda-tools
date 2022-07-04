"""List items on Overmap tile."""
import argparse
import os.path
import sys

from .. import json
from . import Command, util


class List(Command):
    """List items on Overmap tile."""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "list",
            help="List things at an overmap position (could be considered cheating!).",
            description="List things at an overmap position (could be considered cheating!).",
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
            "x",
            type=str,
            help="x coordinate in overmap format -1'179 "
            '(quote neg. numbers, with a space: " -1\'32")',
        )
        parser.add_argument(
            "y",
            type=str,
            help="y coordinate in overmap format -1'179",
        )
        parser.add_argument(
            "--z-levels",
            "-z",
            type=int,
            nargs="+",
            default=list(range(-10, 11)),
            help="restrict to z-levels",
        )

    def exec(self, arg):
        # pylint: disable=too-many-locals

        world_dir = util.get_world_path(arg.dir, arg.world)

        for level in arg.z_levels:
            if level < -10 or level > 10:
                print(
                    "Unsupported z level: {}. Must be in range [-10, 10]".format(
                        level,
                    )
                )
                sys.exit(1)

        x_parts = list(map(int, arg.x.split("'")))
        y_parts = list(map(int, arg.y.split("'")))

        map_x, map_y = util.coord_to_map(*x_parts, *y_parts)
        chunk_x, chunk_y = util.map_to_chunk(map_x, map_y)
        map_files = [
            os.path.join(
                world_dir,
                util.MAPS_DIR,
                "{}.{}.{}".format(chunk_x, chunk_y, z),
                "{}.{}.{}.map".format(map_x, map_y, z),
            )
            for z in arg.z_levels
        ]

        collect = {}

        for file in map_files:
            if not os.path.isfile(file):
                continue

            map_json = json.read_json(file)
            for map_chunk in map_json:
                items = map_chunk["items"]
                for i in range(len(items) // 3):
                    items_here = items[i * 3 + 2]
                    item_id = ""
                    count = 1
                    for item in items_here:
                        if isinstance(item, list):
                            item_id = item[0]["typeid"]
                            count = item[1]
                        else:
                            item_id = item["typeid"]

                    if item_id in collect:
                        collect[item_id] += count
                    else:
                        collect[item_id] = count

        keys = list(collect.keys())
        keys.sort()
        for k in keys:
            print("{} ({})".format(k, collect[k]))
