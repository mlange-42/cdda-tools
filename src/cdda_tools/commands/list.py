import argparse
import os.path

from . import Command, util


class List(Command):
    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "list",
            help="List things at an overmap position.",
            description="List things at an overmap position.",
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
            help="x coordinate in overmap format -1'179 (quote neg. numbers, with a space: \" -1'32\")",
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
        world_dir = util.get_world_path(arg.dir, arg.world)

        for l in arg.z_levels:
            if l < -10 or l > 10:
                print(
                    "Unsupported z level: {}. Must be in range [-10, 10]".format(
                        l,
                    )
                )
                exit(1)

        x_parts = list(map(int, arg.x.split("'")))
        y_parts = list(map(int, arg.y.split("'")))

        x, y = util.coord_to_map(*x_parts, *y_parts)
        cx, cy = util.map_to_chunk(x, y)
        map_files = [
            os.path.join(
                world_dir,
                util.MAPS_DIR,
                "{}.{}.{}".format(cx, cy, z),
                "{}.{}.{}".format(x, y, z),
            )
            for z in arg.z_levels
        ]

        print(map_files)
