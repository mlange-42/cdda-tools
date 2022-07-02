from os import path
import argparse
import glob
import regex
from fnmatch import translate

from . import Command, util
from .. import json


class Notes(Command):
    def add_subcommand(self, subparsers):
        parser_copy_player = subparsers.add_parser(
            "notes",
            help="Edit overmap notes.",
            description="Edit overmap notes.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_copy_player.add_argument(
            "--world",
            "-w",
            type=str,
            required=True,
            help="the game world to copy from",
        )
        parser_copy_player.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to modify notes for, optional if only one player in world",
        )

        subparsers = parser_copy_player.add_subparsers(
            help="Notes sub-commands",
            dest="notes_subparser",
        )

        parser_filter = subparsers.add_parser(
            "delete",
            help="Delete overmap notes by pattern.",
            description="Delete overmap notes by pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_filter.add_argument(
            "pattern",
            type=str,
            nargs="*",
            help="glob pattern to filter out notes",
        )

        parser_list = subparsers.add_parser(
            "list",
            help="List overmap notes by pattern.",
            description="List overmap notes by pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_list.add_argument(
            "pattern",
            type=str,
            nargs="*",
            help="glob pattern to list notes",
        )

        parser_danger = subparsers.add_parser(
            "danger",
            help="Mark overmap notes as dangerous, by symbol or text.",
            description="Mark overmap notes as dangerous, by symbol or text.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_danger.add_argument(
            "pattern",
            type=str,
            nargs="*",
            help="glob pattern to mark notes",
        )

        parser_danger.add_argument(
            "--radius",
            "-r",
            type=int,
            default=2,
            help="autotravel avoidance radius, use negative value to un-mark danger; default 2",
        )


    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        save, save_name, player = util.get_save_path(world_dir, arg.player)

        print(
            "Processing notes for {} ({})".format(
                player, world_dir,
            )
        )

        seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))

        if arg.notes_subparser == "list":
            list_notes(seen_files, arg.pattern)
        elif arg.notes_subparser == "delete":
            delete_notes(seen_files, arg.pattern)
        elif arg.notes_subparser == "danger":
            mark_notes_danger(seen_files, arg.pattern, arg.radius)
        else:
            print("Unknown notes sub-command '{}'.".format(arg.notes_subparser))
            exit(1)


def matches(string, regex_arr):
    for re in regex_arr:
        if regex.match(re, string):
            return True
    return False


def list_notes(seen_files, patterns):
    rex = [regex.compile(translate(p)) for p in patterns]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        for i in range(len(notes)):
            for n in notes[i]:
                if matches(n[2], rex):
                    print(n[2])


def mark_notes_danger(seen_files, patterns, radius):
    rex = [regex.compile(translate(p)) for p in patterns]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for i in range(len(notes)):
            for n in notes[i]:
                if matches(n[2], rex):
                    if radius < 0:
                        n[3] = False
                        n[4] = 0
                    else:
                        n[3] = True
                        n[4] = radius
                    file_changed = True
                    print(n[2])
        if file_changed:
            json.write_json(content, file)


def delete_notes(seen_files, patterns):
    rex = [regex.compile(translate(p)) for p in patterns]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for i in range(len(notes)):
            for n in notes[i]:
                if matches(n[2], rex):
                    print(n[2])
            old_size = len(notes[i])
            notes[i] = list(filter(lambda n: not matches(n[2], rex), notes[i]))
            if len(notes[i]) < old_size:
                file_changed = True
        if file_changed:
            json.write_json(content, file)

