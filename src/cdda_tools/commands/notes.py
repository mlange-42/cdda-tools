from os import path
import argparse
import glob
import regex
from fnmatch import translate

from . import Command, util
from .. import json

IS_WHITESPACE = regex.compile("[ :;]")
IS_NOT_WHITESPACE = regex.compile("[^ :;]")


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
            nargs="+",
            help="glob pattern to delete notes",
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
            nargs="+",
            help="glob pattern to list notes",
        )

        parser_list.add_argument(
            "--danger",
            "-d",
            action="store_true",
            help="list only dangerous notes",
        )

        parser_danger = subparsers.add_parser(
            "danger",
            help="Mark/unmark overmap notes as dangerous, by symbol or text.",
            description="Mark/unmark overmap notes as dangerous, by symbol or text.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_danger.add_argument(
            "pattern",
            type=str,
            nargs="+",
            help="glob pattern to mark notes",
        )

        parser_danger.add_argument(
            "--radius",
            "-r",
            type=int,
            default=2,
            help="autotravel avoidance radius, use negative value to un-mark danger; default 2",
        )

        parser_edit = subparsers.add_parser(
            "edit",
            help="Edit note symbol, color or text, by symbol or text.",
            description="Edit note symbol, color or text, by symbol or text.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser_edit.add_argument(
            "pattern",
            type=str,
            nargs="+",
            help="glob pattern to edit notes",
        )
        parser_edit.add_argument(
            "--symbol", "-s", type=str, nargs=1, help="symbol to set; optional"
        )
        parser_edit.add_argument(
            "--color", "-c", type=str, nargs=1, help="color letter(s) to set; optional"
        )
        parser_edit.add_argument(
            "--text", "-t", type=str, nargs=1, help="text set; optional"
        )

    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        save, save_name, player = util.get_save_path(world_dir, arg.player)

        print(
            "Processing notes for {} ({})".format(
                player,
                world_dir,
            )
        )

        seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))

        if arg.notes_subparser == "list":
            list_notes(seen_files, arg.pattern, arg.danger)
        elif arg.notes_subparser == "delete":
            delete_notes(seen_files, arg.pattern)
        elif arg.notes_subparser == "danger":
            mark_notes_danger(seen_files, arg.pattern, arg.radius)
        elif arg.notes_subparser == "edit":
            edit_notes(seen_files, arg.pattern, arg.symbol, arg.color, arg.text)
        else:
            print("Unknown notes sub-command '{}'.".format(arg.notes_subparser))
            exit(1)


def matches(string, regex_arr):
    for re in regex_arr:
        if regex.match(re, string):
            return True
    return False


def print_note(note):
    print(
        "{}{:3} | {:3} {:3} | {}".format(
            "!" if note[3] else " ",
            note[4] if note[3] else " ",
            note[0],
            note[1],
            note[2],
        )
    )


def list_notes(seen_files, patterns, danger):
    rex = [regex.compile(translate(p)) for p in patterns]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        for i in range(len(notes)):
            for n in notes[i]:
                if (not danger or n[3]) and matches(n[2], rex):
                    print_note(n)


def edit_notes(seen_files, patterns, symbol, color, text):
    if symbol is None and color is None and text is None:
        print(
            "Notes sub-command 'edit' requires at least one of options --symbol/-s, --color/-c, --text/-t"
        )
        exit(1)

    rex = [regex.compile(translate(p)) for p in patterns]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for i in range(len(notes)):
            for n in notes[i]:
                if matches(n[2], rex):
                    print_note(n)
                    _edit_note(n[2], symbol, color, text)
        if file_changed:
            json.write_json(content, file)


def _edit_note(note: str, symbol, color, text):
    tup = note_tuple(note)
    print(tup)


def note_tuple(note):
    """(note symbol, note color, offset to text)"""
    result = ["N", None, 0]
    set_color = False
    set_symbol = False

    pos = 0
    for i in range(2):
        pos = regex.search(IS_NOT_WHITESPACE, note, pos=pos, endpos=5)
        if pos is None:
            return result
        else:
            pos = pos.span()[0]

        end = regex.search(IS_WHITESPACE, note, pos=pos, endpos=5)
        if end is None:
            return result
        else:
            end = end.span()[0]

        if not set_symbol and note[end] == ":":
            result[0] = note[end - 1]
            result[2] = end + 1
            set_symbol = True
        elif not set_color and note[end] == ";":
            result[1] = note[pos:end]
            result[2] = end + 1
            set_color = True

        pos = end + 1

    return result


def format_note_tuple(tup, note):
    if tup[1] is None:
        return "{}:{}".format(tup[0], note[tup[2] :])
    else:
        return "{}:{};{}".format(tup[0], tup[1], note[tup[2] :])


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
                    print_note(n)
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
                    print_note(n)
            old_size = len(notes[i])
            notes[i] = list(filter(lambda n: not matches(n[2], rex), notes[i]))
            if len(notes[i]) < old_size:
                file_changed = True
        if file_changed:
            json.write_json(content, file)
