import argparse
import glob
import os
from fnmatch import translate
from os import path

import regex

from .. import json
from . import Command, util

IS_WHITESPACE = regex.compile("[ :;]")
IS_NOT_WHITESPACE = regex.compile("[^ :;]")


class Notes(Command):
    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "notes",
            help="Edit overmap notes.",
            description="Edit overmap notes.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser.add_argument(
            "--world",
            "-w",
            type=str,
            required=True,
            help="the game world to copy from",
        )
        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to modify notes for, optional if only one player in world",
        )

        subparsers = parser.add_subparsers(
            help="Notes sub-commands",
            dest="notes_subparser",
        )
        self._add_parser_list(subparsers)
        self._add_parser_delete(subparsers)
        self._add_parser_danger(subparsers)
        self._add_parser_edit(subparsers)
        self._add_parser_replace(subparsers)

    def _add_parser_list(self, subparsers):
        parser_list = subparsers.add_parser(
            "list",
            help="List overmap notes by pattern.",
            description="List overmap notes by pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser_list.add_argument(
            "patterns",
            type=str,
            nargs="+",
            help="glob patterns to list notes",
        )
        parser_list.add_argument(
            "--ignore",
            "-i",
            type=str,
            nargs="*",
            help="glob patterns to ignore notes",
        )
        parser_list.add_argument(
            "--case",
            "-C",
            action="store_true",
            help="case-sensitive glob pattern",
        )
        parser_list.add_argument(
            "--danger",
            "-d",
            action="store_true",
            help="list only dangerous notes",
        )

    def _add_parser_delete(self, subparsers):
        parser_delete = subparsers.add_parser(
            "delete",
            help="Delete overmap notes by pattern.",
            description="Delete overmap notes by pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser_delete.add_argument(
            "patterns",
            type=str,
            nargs="+",
            help="glob patterns to delete notes",
        )
        parser_delete.add_argument(
            "--ignore",
            "-i",
            type=str,
            nargs="*",
            help="glob patterns to ignore notes",
        )
        parser_delete.add_argument(
            "--case",
            "-C",
            action="store_true",
            help="case-sensitive glob pattern",
        )
        parser_delete.add_argument(
            "--dry",
            action="store_true",
            help="dry-run (don't save changes)",
        )

    def _add_parser_danger(self, subparsers):
        parser_danger = subparsers.add_parser(
            "danger",
            help="Mark/unmark overmap notes as dangerous, by pattern.",
            description="Mark/unmark overmap notes as dangerous, by pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser_danger.add_argument(
            "patterns",
            type=str,
            nargs="+",
            help="glob patterns to mark notes",
        )
        parser_danger.add_argument(
            "--ignore",
            "-i",
            type=str,
            nargs="*",
            help="glob patterns to ignore notes",
        )
        parser_danger.add_argument(
            "--case",
            "-C",
            action="store_true",
            help="case-sensitive glob pattern",
        )
        parser_danger.add_argument(
            "--radius",
            "-r",
            type=int,
            default=2,
            help="autotravel avoidance radius, use negative value to un-mark danger; default 2",
        )
        parser_danger.add_argument(
            "--dry",
            action="store_true",
            help="dry-run (don't save changes)",
        )

    def _add_parser_edit(self, subparsers):
        parser_edit = subparsers.add_parser(
            "edit",
            help="Edit note symbol, color or text, by pattern.",
            description="Edit note symbol, color or text, by pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser_edit.add_argument(
            "patterns",
            type=str,
            nargs="+",
            help="glob patterns to edit notes",
        )
        parser_edit.add_argument(
            "--ignore",
            "-i",
            type=str,
            nargs="*",
            help="glob patterns to ignore notes",
        )
        parser_edit.add_argument(
            "--case",
            "-C",
            action="store_true",
            help="case-sensitive glob pattern",
        )
        parser_edit.add_argument(
            "--symbol", "-s", type=str, help="symbol to set; optional"
        )
        parser_edit.add_argument(
            "--color", "-c", type=str, help="color letter(s) to set; optional"
        )
        parser_edit.add_argument("--text", "-t", type=str, help="text set; optional")
        parser_edit.add_argument(
            "--dry",
            action="store_true",
            help="dry-run (don't save changes)",
        )

    def _add_parser_replace(self, subparsers):
        parser_edit = subparsers.add_parser(
            "replace",
            help="Full-text replacement, in notes matching pattern.",
            description="Full-text replacement, in notes matching pattern.",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser_edit.add_argument(
            "patterns",
            type=str,
            nargs="+",
            help="glob patterns to filter notes",
        )
        parser_edit.add_argument(
            "--ignore",
            "-i",
            type=str,
            nargs="*",
            help="glob patterns to ignore notes",
        )
        parser_edit.add_argument(
            "--case",
            "-c",
            action="store_true",
            help="case-sensitive glob pattern",
        )
        parser_edit.add_argument(
            "--replace",
            "-r",
            type=str,
            help="pairs of text to search, and replacement",
            required=True,
            nargs="+",
        )
        parser_edit.add_argument(
            "--dry",
            action="store_true",
            help="dry-run (don't save changes)",
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
            list_notes(seen_files, arg.patterns, arg.ignore, arg.danger, arg.case)
        elif arg.notes_subparser == "delete":
            delete_notes(seen_files, arg.patterns, arg.ignore, arg.case, arg.dry)
        elif arg.notes_subparser == "danger":
            mark_notes_danger(
                seen_files, arg.patterns, arg.ignore, arg.radius, arg.case, arg.dry
            )
        elif arg.notes_subparser == "edit":
            edit_notes(
                seen_files,
                arg.patterns,
                arg.ignore,
                arg.symbol,
                arg.color,
                arg.text,
                arg.case,
                arg.dry,
            )
        elif arg.notes_subparser == "replace":
            replace_in_notes(
                seen_files, arg.patterns, arg.ignore, arg.replace, arg.case, arg.dry
            )
        else:
            print("Unknown notes sub-command '{}'.".format(arg.notes_subparser))
            exit(1)


def matches(text, regex_arr, case_sensitive):
    if not case_sensitive:
        text = os.path.normcase(text)
    for re in regex_arr:
        if regex.match(re, text):
            return True
    return False


def _compile_regex(pat, case_sensitive):
    if not case_sensitive:
        pat = os.path.normcase(pat)

    return regex.compile(translate(pat))


def _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, func):
    rex = [_compile_regex(p, case_sensitive) for p in patterns]
    rex_ign = [_compile_regex(p, case_sensitive) for p in ignore or []]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for i in range(len(notes)):
            for n in notes[i]:
                if matches(n[2], rex, case_sensitive) and not matches(
                    n[2], rex_ign, case_sensitive
                ):
                    file_changed = func(n)
        if file_changed and not dry:
            json.write_json(content, file)


def list_notes(seen_files, patterns, ignore, danger, case_sensitive):
    def handle(note):
        if not danger or note[3]:
            print(util.note_to_str(note))
        return False

    _handle_notes(seen_files, patterns, ignore, case_sensitive, True, handle)


def edit_notes(seen_files, patterns, ignore, symbol, color, text, case_sensitive, dry):
    if symbol is None and color is None and text is None:
        print(
            "Notes sub-command 'edit' requires at least one of options --symbol/-s, --color/-c, --text/-t"
        )
        exit(1)

    if symbol is not None and len(symbol) != 1:
        print("Symbol argument must be a single character!")
        exit(1)

    if color is not None and (len(color) < 1 or len(color) > 2):
        print("Color argument must be a string of 1 or 2 characters!")
        exit(1)

    def handle(note):
        print(util.note_to_str(note))
        note[2] = _edit_note(note[2], symbol, color, text)
        print(util.note_to_str(note))
        print("-----------------------------------------")
        return True

    _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, handle)


def _edit_note(note: str, symbol, color, text):
    tup = note_tuple(note)
    if symbol is not None:
        tup[0] = symbol
    if color is not None:
        tup[1] = color
    if text is not None:
        note = "{}{}".format(note[: tup[2]], text)

    return format_note_tuple(tup, note)


def _replace_in_note(note: str, replace):
    tup = note_tuple(note)
    for r in range(0, len(replace), 2):
        text = note[tup[2] :]
        text = text.replace(replace[r], replace[r + 1])
        note = "{}{}".format(note[: tup[2]], text)

    return format_note_tuple(tup, note)


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


def replace_in_notes(seen_files, patterns, ignore, replace, case_sensitive, dry):
    if len(replace) % 2 != 0:
        print(
            "Option --replace requires an even number of arguments (search/replace pairs)"
        )
        exit(1)

    def handle(note):
        print(util.note_to_str(note))
        note[2] = _replace_in_note(note[2], replace)
        print(util.note_to_str(note))
        print("-----------------------------------------")
        return True

    _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, handle)


def format_note_tuple(tup, note):
    if tup[1] is None:
        return "{}:{}".format(tup[0], note[tup[2] :])
    else:
        return "{}:{};{}".format(tup[0], tup[1], note[tup[2] :])


def mark_notes_danger(seen_files, patterns, ignore, radius, case_sensitive, dry):
    def handle(note):
        if radius < 0:
            note[3] = False
            note[4] = 0
        else:
            note[3] = True
            note[4] = radius
        print(util.note_to_str(note))
        return True

    _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, handle)


def delete_notes(seen_files, patterns, ignore, case_sensitive, dry):
    rex = [_compile_regex(p, case_sensitive) for p in patterns]
    rex_ign = [_compile_regex(p, case_sensitive) for p in ignore or []]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for i in range(len(notes)):
            for n in notes[i]:
                if matches(n[2], rex, case_sensitive) and not matches(
                    n[2], rex_ign, case_sensitive
                ):
                    print(util.note_to_str(n))
            old_size = len(notes[i])
            notes[i] = list(
                filter(
                    lambda n: not (
                        matches(n[2], rex, case_sensitive)
                        and not matches(n[2], rex_ign, case_sensitive)
                    ),
                    notes[i],
                )
            )
            if len(notes[i]) < old_size:
                file_changed = True
        if file_changed and not dry:
            json.write_json(content, file)
