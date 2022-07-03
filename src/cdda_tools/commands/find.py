from os import path
import argparse
import glob
from fnmatch import translate
import regex

from . import Command, util
from .. import json


class Find(Command):
    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "find",
            help="Find terrain or items.",
            description="Find terrain or items.",
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
            "--player",
            "-p",
            type=str,
            help="the player to rearch for",
        )

        subparsers = parser.add_subparsers(
            help="Find sub-commands",
            dest="find_subparser",
        )

        self._add_parser_terrain(subparsers)

    def _add_parser_terrain(self, subparsers):
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
        parser_terrain.add_argument(
            "--z-levels",
            "-z",
            type=int,
            nargs="+",
            default=list(range(-10, 11)),
            help="restrict to z-levels",
        )
        parser_terrain.add_argument(
            "--unseen",
            "-U",
            action="store_true",
            help="search also for unseen terrain",
        )

    def exec(self, arg):
        if arg.find_subparser == "terrain":
            find_terrain(arg)
        else:
            print("Unknown find sub-command '{}'.".format(arg.find_subparser))
            exit(1)


def _is_seen(seen_layer, index):
    pos = 0
    for seen, le in seen_layer:
        if index < pos + le:
            return seen
        pos += le
    raise ValueError("Index {} out of range of seen layer (len=pos).".format(index))


def find_terrain(arg):
    for l in arg.z_levels:
        if l < -10 or l > 10:
            print(
                "Unsupported z level: {}. Must be in range [-10, 10]".format(
                    l,
                )
            )
            exit(1)

    world_dir = util.get_world_path(arg.dir, arg.world)
    save, save_name, player = util.get_save_path(world_dir, arg.player)

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

    for map_file, seen_file, xy in zip(files_overmap, seen_files, seen_coords):
        map_json = json.read_json(map_file)
        seen_json = json.read_json(seen_file)
        layers = map_json["layers"]
        seen_layers = seen_json["visible"]
        for l in arg.z_levels:
            layer = layers[l + 10]
            seen_layer = seen_layers[l + 10]
            pos = 0
            for rle in layer:
                match = False
                for re in rex:
                    if regex.match(re, rle[0]):
                        match = True
                        break
                if match:
                    for i in range(rle[1]):
                        index = pos + i
                        if arg.unseen or _is_seen(seen_layer, index):
                            xx, yy = util.index_to_xy_overmap(index)
                            print(
                                "{}'{}, {}'{}, {}: {}".format(
                                    xy[0], xx, xy[1], yy, l, rle[0]
                                )
                            )
                pos += rle[1]
