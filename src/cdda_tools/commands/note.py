import argparse
from os import path

from .. import json
from . import Command, util


class Note(Command):
    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "note",
            help="Add an overmap note.",
            description="Add an overmap note.",
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
            "z",
            type=int,
            help="z coordinate in overmap format -1'179",
        )
        parser.add_argument(
            "symbol",
            type=str,
            help="note symbol",
        )
        parser.add_argument(
            "color",
            type=str,
            help="note color letter(s)",
        )
        parser.add_argument(
            "note",
            type=str,
            nargs="+",
            help="note text",
        )
        parser.add_argument(
            "--danger",
            dest="radius",
            type=int,
            help="mark as dangerous, with given avoidance radius",
        )
        parser.add_argument(
            "--dry",
            action="store_true",
            help="dry-run (don't save changes)",
        )

    def exec(self, arg):
        if arg.z < -10 or arg.z > 10:
            print(
                "Unsupported z level: {}. Must be in range [-10, 10]".format(
                    arg.z,
                )
            )
            exit(1)

        if len(arg.symbol) != 1:
            print("Note symbol must be exactly one character")
            exit(1)

        if len(arg.color) < 1 or len(arg.color) > 2:
            print("Note color argument must be a string of 1 or 2 characters!")
            exit(1)

        world_dir = util.get_world_path(arg.dir, arg.world)
        save, save_name, player = util.get_save_path(world_dir, arg.player)

        text = " ".join(arg.note)
        x_parts = list(map(int, arg.x.split("'")))
        y_parts = list(map(int, arg.y.split("'")))

        seen_file = path.join(
            world_dir, "{}.seen.{}.{}".format(save_name, x_parts[0], y_parts[0])
        )

        content = json.read_json(seen_file)
        notes = content["notes"]
        new_note = [
            x_parts[1],
            y_parts[1],
            "{}:{};{}".format(arg.symbol, arg.color, text),
            arg.radius is not None,
            arg.radius or 0,
        ]
        print(util.note_to_str(new_note))
        notes[arg.z + 10].append(new_note)

        if not arg.dry:
            json.write_json(content, seen_file)
