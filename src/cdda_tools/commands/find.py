import fnmatch
import os
from os import path
import argparse
import glob
from fnmatch import fnmatchcase, translate
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
        parser.add_argument(
            "--terrain",
            "-t",
            type=str,
            nargs="+",
            help="search terrain by glob pattern(s)",
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
            "Searching for {} in {} ({})".format(
                arg.terrain,
                player,
                world_dir,
            )
        )

        seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))
        seen_coords = [list(map(int, f.split(".")[-2:])) for f in seen_files]
        files_overmap = [
            path.join(world_dir, "o.{}.{}".format(*xy)) for xy in seen_coords
        ]

        rex = [regex.compile(translate(pat)) for pat in arg.terrain]

        for map_file, seen_file, xy in zip(files_overmap, seen_files, seen_coords):
            map_json = json.read_json(map_file)
            layers = map_json["layers"]
            for l in arg.z_levels:
                layer = layers[l + 10]
                pos = 0
                for rle in layer:
                    match = False
                    for re in rex:
                        if regex.match(re, rle[0]):
                            match = True
                            break
                    if match:
                        for i in range(rle[1]):
                            xx, yy = util.index_to_xy_overmap(pos + i)
                            print(
                                "{}'{}, {}'{}, {}: {}".format(
                                    xy[0], xx, xy[1], yy, l, rle[0]
                                )
                            )
                    pos += rle[1]
