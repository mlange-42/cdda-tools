"""View and manipulate Overmap notes."""
import argparse
import glob
import os
from fnmatch import translate
from os import path

import regex

from .. import json_utils as json
from . import Command, util

IS_WHITESPACE = regex.compile("[ :;]")
IS_NOT_WHITESPACE = regex.compile("[^ :;]")


class Notes(Command):
    """View and manipulate Overmap notes."""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "notes",
            help="Edit overmap notes.",
            description="Edit overmap notes.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world to search in")

        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to modify notes for, optional if only one player in world",
        )

        subparsers = parser.add_subparsers(
            help="Notes sub-commands",
            dest="notes_subcommand",
            required=True,
        )
        _add_parser_list(subparsers)
        _add_parser_delete(subparsers)
        _add_parser_danger(subparsers)
        _add_parser_edit(subparsers)
        _add_parser_replace(subparsers)

    def exec(self, arg):
        world_dir = util.get_world_path(arg.dir, arg.world)
        _, save_name, _ = util.get_save_path(world_dir, arg.player)

        seen_files = glob.glob(path.join(world_dir, "{}.seen.*.*".format(save_name)))

        if arg.notes_subcommand == "list":
            yield from list_notes(
                seen_files, arg.patterns, arg.ignore, arg.danger, arg.case
            )
        elif arg.notes_subcommand == "delete":
            yield from delete_notes(
                seen_files, arg.patterns, arg.ignore, arg.case, arg.dry
            )
        elif arg.notes_subcommand == "danger":
            yield from mark_notes_danger(
                seen_files, arg.patterns, arg.ignore, arg.radius, arg.case, arg.dry
            )
        elif arg.notes_subcommand == "edit":
            yield from edit_notes(
                seen_files,
                arg.patterns,
                arg.ignore,
                arg.symbol,
                arg.color,
                arg.text,
                arg.case,
                arg.dry,
            )
        elif arg.notes_subcommand == "replace":
            yield from replace_in_notes(
                seen_files, arg.patterns, arg.ignore, arg.replace, arg.case, arg.dry
            )
        else:
            raise ValueError(
                "Unknown notes sub-command '{}'. Try:\n"
                "  cdda_tools notes --help".format(arg.notes_subparser)
            )


def matches(text, regex_arr, case_sensitive):
    """Test if a string marches RegEx"""
    if not case_sensitive:
        text = os.path.normcase(text)
    for reg in regex_arr:
        if regex.match(reg, text):
            return True
    return False


def _compile_regex(pat, case_sensitive):
    """Compile RegEx"""
    if not case_sensitive:
        pat = os.path.normcase(pat)

    return regex.compile(translate(pat))


# pylint: disable=too-many-arguments
def _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, func):
    # pylint: disable=too-many-locals
    rex = [_compile_regex(p, case_sensitive) for p in patterns]
    rex_ign = [_compile_regex(p, case_sensitive) for p in ignore or []]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for note_layer in notes:
            for note in note_layer:
                if matches(note[2], rex, case_sensitive) and not matches(
                    note[2], rex_ign, case_sensitive
                ):
                    lines, file_changed = func(note)
                    for line in lines:
                        yield line
        if file_changed and not dry:
            json.write_json(content, file)


def list_notes(seen_files, patterns, ignore, danger, case_sensitive):
    """List notes by pattern"""

    def handle(note):
        lines = []
        if not danger or note[3]:
            lines.append(util.note_to_str(note))
        return lines, False

    yield from _handle_notes(seen_files, patterns, ignore, case_sensitive, True, handle)


# pylint: disable=too-many-arguments
def edit_notes(seen_files, patterns, ignore, symbol, color, text, case_sensitive, dry):
    """Edit notes by pattern"""
    if symbol is None and color is None and text is None:
        raise ValueError(
            "Notes sub-command 'edit' requires at least one of options"
            " --symbol/-s, --color/-c, --text/-t"
        )

    if symbol is not None and len(symbol) != 1:
        raise ValueError("Symbol argument must be a single character!")

    if color is not None and (len(color) < 1 or len(color) > 2):
        raise ValueError("Color argument must be a string of 1 or 2 characters!")

    def handle(note):
        lines = [util.note_to_str(note)]
        note[2] = _edit_note(note[2], symbol, color, text)
        lines.append(util.note_to_str(note))
        lines.append("-----------------------------------------")
        return lines, True

    yield from _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, handle)


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
    for i in range(0, len(replace), 2):
        text = note[tup[2] :]
        text = text.replace(replace[i], replace[i + 1])
        note = "{}{}".format(note[: tup[2]], text)

    return format_note_tuple(tup, note)


def note_tuple(note):
    """(note symbol, note color, offset to text)"""
    result = ["N", None, 0]
    set_color = False
    set_symbol = False

    pos = 0
    for _ in range(2):
        pos = regex.search(IS_NOT_WHITESPACE, note, pos=pos, endpos=5)
        if pos is None:
            return result

        pos = pos.span()[0]

        end = regex.search(IS_WHITESPACE, note, pos=pos, endpos=5)
        if end is None:
            return result

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
    """Full-text replace in notes by pattern"""
    if len(replace) % 2 != 0:
        raise ValueError(
            "Option --replace requires an even number of arguments (search/replace pairs)"
        )

    def handle(note):
        lines = [util.note_to_str(note)]
        note[2] = _replace_in_note(note[2], replace)
        lines.append(util.note_to_str(note))
        lines.append("-----------------------------------------")
        return lines, True

    yield from _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, handle)


def format_note_tuple(tup, note):
    """Format note tuple to text"""
    if tup[1] is None:
        return "{}:{}".format(tup[0], note[tup[2] :])

    return "{}:{};{}".format(tup[0], tup[1], note[tup[2] :])


def mark_notes_danger(seen_files, patterns, ignore, radius, case_sensitive, dry):
    """Mark notes as dangerous by pattern"""

    def handle(note):
        if radius < 0:
            note[3] = False
            note[4] = 0
        else:
            note[3] = True
            note[4] = radius
        return [util.note_to_str(note)], True

    yield from _handle_notes(seen_files, patterns, ignore, case_sensitive, dry, handle)


def delete_notes(seen_files, patterns, ignore, case_sensitive, dry):
    """Delete notes by pattern"""
    rex = [_compile_regex(p, case_sensitive) for p in patterns]
    rex_ign = [_compile_regex(p, case_sensitive) for p in ignore or []]
    for file in seen_files:
        content = json.read_json(file)
        notes = content["notes"]
        file_changed = False
        for i, note_layer in enumerate(notes):
            for note in note_layer:
                if matches(note[2], rex, case_sensitive) and not matches(
                    note[2], rex_ign, case_sensitive
                ):
                    yield util.note_to_str(note)
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


def _add_parser_list(subparsers):
    parser_list = subparsers.add_parser(
        "list",
        help="List overmap notes by pattern.",
        description="List overmap notes by pattern.\n\n"
        "Examples:\n\n"
        "  cdda_tools notes -w MyWorld -p MyPlayer list *\n"
        "  cdda_tools notes -w MyWorld -p MyPlayer list *moose*",
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


def _add_parser_delete(subparsers):
    parser_delete = subparsers.add_parser(
        "delete",
        help="Delete overmap notes by pattern.",
        description="Delete overmap notes by pattern.\n\n"
        "Examples:\n\n"
        '  cdda_tools notes -w MyWorld -p MyPlayer delete "*Dead Vegetation*"',
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
    util.add_dry_run_options(parser_delete)


def _add_parser_danger(subparsers):
    parser_danger = subparsers.add_parser(
        "danger",
        help="Mark/unmark overmap notes as dangerous, by pattern.",
        description="Mark/unmark overmap notes as dangerous, by pattern.\n\n"
        "Examples:\n\n"
        "  cdda_tools notes -w MyWorld -p MyPlayer danger *moose* --radius 2",
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
    util.add_dry_run_options(parser_danger)


def _add_parser_edit(subparsers):
    parser_edit = subparsers.add_parser(
        "edit",
        help="Edit note symbol, color or text, by pattern.",
        description="Edit note symbol, color or text, by pattern.\n\n"
        "Examples:\n\n"
        "  cdda_tools notes -w MyWorld -p MyPlayer edit *moose* --symbol ! --color R",
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
    parser_edit.add_argument("--symbol", "-s", type=str, help="symbol to set; optional")
    parser_edit.add_argument(
        "--color", "-c", type=str, help="color letter(s) to set; optional"
    )
    parser_edit.add_argument("--text", "-t", type=str, help="text set; optional")
    util.add_dry_run_options(parser_edit)


def _add_parser_replace(subparsers):
    parser_replace = subparsers.add_parser(
        "replace",
        help="Full-text replacement, in notes matching pattern.",
        description="Full-text replacement, in notes matching pattern.\n\n"
        "Examples:\n\n"
        "  cdda_tools notes -w MyWorld -p MyPlayer replace * --replace moose !MOOSE! Moose !MOOSE!",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser_replace.add_argument(
        "patterns",
        type=str,
        nargs="+",
        help="glob patterns to filter notes",
    )
    parser_replace.add_argument(
        "--ignore",
        "-i",
        type=str,
        nargs="*",
        help="glob patterns to ignore notes",
    )
    parser_replace.add_argument(
        "--case",
        "-c",
        action="store_true",
        help="case-sensitive glob pattern",
    )
    parser_replace.add_argument(
        "--replace",
        "-r",
        type=str,
        help="pairs of text to search, and replacement",
        required=True,
        nargs="+",
    )
    util.add_dry_run_options(parser_replace)
