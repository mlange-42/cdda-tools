"""Find Overmap features"""
import argparse
import glob
from fnmatch import translate
from os import path

import regex

from .. import json_utils as json
from . import Command, util


class Find(Command):
    """Find Overmap features"""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "find",
            help="Find terrain or items.",
            description="Find terrain or items.\n\n"
            "Example:\n\n"
            "  cdda_tools find -w MyWorld -p MyPlayer terrain *subway* -z 0",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world search in")

        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to search for",
        )

        subparsers = parser.add_subparsers(
            help="Find sub-commands",
            dest="find_subparser",
        )

        _add_parser_terrain(subparsers)

    def exec(self, arg):
        if arg.find_subparser == "terrain":
            find_terrain(arg)
        else:
            raise ValueError(
                "Unknown find sub-command '{}'.".format(arg.find_subparser)
            )


def _add_parser_terrain(subparsers):
    parser_terrain = subparsers.add_parser(
        "terrain",
        help="Find overmap terrain types by glob patterns.",
        description="Find overmap terrain types by glob patterns.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser_terrain.add_argument(
        "patterns",
        type=str,
        nargs="+",
        help="glob patterns to search for",
    )

    util.add_z_level_options(parser_terrain)

    parser_terrain.add_argument(
        "--unseen",
        "-U",
        action="store_true",
        help="search also for unseen terrain (could be considered cheating!)",
    )


def _is_seen(seen_layer, index):
    pos = 0
    for seen, run_length in seen_layer:
        if index < pos + run_length:
            return seen
        pos += run_length
    raise ValueError("Index {} out of range of seen layer (len=pos).".format(index))


def find_terrain(arg):
    """Execute the find terrain command"""
    # pylint: disable=too-many-locals
    util.check_levels(arg.z_levels)

    world_dir = util.get_world_path(arg.dir, arg.world)
    _, save_name, player = util.get_save_path(world_dir, arg.player)

    print(
        "Searching for terrain in {} ({})".format(
            player,
            world_dir,
        )
    )

    seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))
    seen_coords = [list(map(int, f.split(".")[-2:])) for f in seen_files]
    files_overmap = [path.join(world_dir, "o.{}.{}".format(*xy)) for xy in seen_coords]

    rex = [regex.compile(translate(pat)) for pat in arg.patterns]

    # pylint: disable=too-many-nested-blocks
    for map_file, seen_file, coord in zip(files_overmap, seen_files, seen_coords):
        map_json = json.read_json(map_file)
        seen_json = json.read_json(seen_file)
        layers = map_json["layers"]
        seen_layers = seen_json["visible"]
        for level in arg.z_levels:
            layer = layers[level + 10]
            seen_layer = seen_layers[level + 10]
            pos = 0
            for rle in layer:
                match = False
                for expr in rex:
                    if regex.match(expr, rle[0]):
                        match = True
                        break
                if match:
                    for i in range(rle[1]):
                        index = pos + i
                        if arg.unseen or _is_seen(seen_layer, index):
                            x_sub, y_sub = util.index_to_xy_overmap(index)
                            print(
                                "{}'{}, {}'{}, {}: {}".format(
                                    coord[0], x_sub, coord[1], y_sub, level, rle[0]
                                )
                            )
                pos += rle[1]
