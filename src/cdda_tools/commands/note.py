"""Add Overmap notes."""
import argparse
from os import path

from .. import json_utils as json
from . import Command, util


class Note(Command):
    """Add Overmap notes."""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "note",
            help="Add an overmap note.",
            description="Add an overmap note.\n\n"
            "Example:\n\n"
            "  cdda_tools note -w MyWorld -p MyPlayer "
            '" -1\'123" 1\'10 0 ! R "Something dangerous" --danger 2',
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world to add a note")

        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to rearch for",
        )

        util.add_xy_options(parser)

        parser.add_argument(
            "z",
            type=int,
            help="z level",
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
            raise ValueError(
                "Unsupported z level: {}. Must be in range [-10, 10]".format(
                    arg.z,
                )
            )

        if len(arg.symbol) != 1:
            raise ValueError("Note symbol must be exactly one character")

        if len(arg.color) < 1 or len(arg.color) > 2:
            raise ValueError(
                "Note color argument must be a string of 1 or 2 characters!"
            )

        world_dir = util.get_world_path(arg.dir, arg.world)
        _, save_name, _ = util.get_save_path(world_dir, arg.player)

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
        yield util.note_to_str(new_note)
        notes[arg.z + 10].append(new_note)

        if not arg.dry:
            json.write_json(content, seen_file)
