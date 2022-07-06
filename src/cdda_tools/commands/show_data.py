"""Show game data."""
import argparse
import json
from fnmatch import translate

import regex

from .. import game
from . import Command


class ShowData(Command):
    """Show game data."""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "show-data",
            help="Show JSON game data by categories and IDs.",
            description="Show JSON game data by categories and IDs.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        subparsers = parser.add_subparsers(
            help="Show data sub-commands",
            dest="show_subparser",
        )

        _add_parser_path(subparsers)
        _add_parser_ids(subparsers)
        _add_parser_pairs(subparsers)

    def exec(self, arg):
        if arg.show_subparser == "path":
            yield from _hierarchical(arg)
        elif arg.show_subparser == "ids":
            yield from _search(arg)
        elif arg.show_subparser == "pairs":
            yield from _pairs(arg)
        else:
            raise ValueError(
                "Unknown show-data sub-command '{}'.".format(arg.show_subparser)
            )


def _add_parser_path(subparsers):
    parser_path = subparsers.add_parser(
        "path",
        help="Show data by JSON path, like (type, id, [property...]).",
        description="Show data by JSON path, like (type, id, [property...]).\n\n"
        "Examples:\n\n"
        "  cdda_tools show-data path TOOL wrench\n"
        "  cdda_tools show-data path TOOL wrench name",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser_path.add_argument(
        "values",
        type=str,
        nargs="*",
        help="key path to print data for",
    )
    parser_path.add_argument(
        "--keys",
        "-k",
        action="store_true",
        help="print only keys, not the complete data",
    )


def _add_parser_ids(subparsers):
    parser_ids = subparsers.add_parser(
        "ids",
        help="print data for IDs matching glob patterns",
        description="print data for IDs matching glob patterns.\n\n"
        "Examples:\n\n"
        "  cdda_tools show-data ids wrench\n"
        "  cdda_tools show-data ids wrench --keys\n"
        "  cdda_tools show-data ids *wrench* --list",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser_ids.add_argument(
        "values",
        type=str,
        nargs="*",
        help="ID glob patterns to search for",
    )
    parser_ids.add_argument(
        "--keys",
        "-k",
        action="store_true",
        help="print only keys, not the complete data",
    )
    parser_ids.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="only list matches, don't print the full data",
    )


def _add_parser_pairs(subparsers):
    parser_pairs = subparsers.add_parser(
        "pairs",
        help="print data for entries with matching key/value pairs",
        description="print data for entries with matching key/value pairs\n\n"
        "Examples:\n\n"
        "  cdda_tools show-data pairs type recipe result *pancake*",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser_pairs.add_argument(
        "values",
        type=str,
        nargs="+",
        help="key/value pairs, key is a property name, value is a glob pattern;\n"
        "multiple pairs are possible and must all match",
    )
    parser_pairs.add_argument(
        "--keys",
        "-k",
        action="store_true",
        help="print only keys, not the complete data",
    )
    parser_pairs.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="only list matches, don't print the full data",
    )


def _hierarchical(arg):
    data = game.read_game_data(arg.dir)
    extract = data
    search_str = "data"

    if arg.values is not None:
        for key in arg.values:
            _check_is_dict(extract, search_str)

            if key in extract:
                extract = extract[key]
            else:
                raise ValueError(f"Id {key} not found in {search_str}")
            search_str += f" --> {key}"

    if arg.keys:
        _check_is_dict(extract, search_str)

        keys = list(extract.keys())
        keys.sort()
        yield keys
    else:
        yield json.dumps(extract, indent=4)


def _search(arg):
    if arg.list and arg.keys:
        raise ValueError("Options --list and --keys are mutually exclusive.")

    data = game.read_game_data(arg.dir)

    rex = [regex.compile(translate(pat)) for pat in arg.values]
    any_found = False
    for cat, entries in data.items():
        if isinstance(entries, dict):
            for key, entry in entries.items():
                match = False
                for expr in rex:
                    if regex.match(expr, key):
                        match = True
                        break
                if match:
                    any_found = True
                    if arg.list:
                        yield f"{key:50} ({cat})"
                    elif arg.keys:
                        yield f"----- Category {cat}: {key} -----"
                        _check_is_dict(entry, f"{cat} --> {key}")

                        keys = list(entry.keys())
                        keys.sort()
                        yield keys
                    else:
                        yield f"----- Category {cat}: {key} -----"
                        yield json.dumps(entry, indent=4)
    if not any_found:
        yield f"No data found for globs {arg.values}"


def _pairs(arg):
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches

    if arg.list and arg.keys:
        raise ValueError("Options --list and --keys are mutually exclusive.")

    if len(arg.values) % 2 != 0:
        raise ValueError(
            "Option 'values' requires an even number of arguments (key/value pairs)."
        )

    data = game.read_game_data(arg.dir)

    conditions = [
        (arg.values[i], regex.compile(translate(arg.values[i + 1])))
        for i in range(0, len(arg.values), 2)
    ]

    any_found = False
    for cat, entries in data.items():
        if isinstance(entries, dict):
            entries_temp = entries.items()
        else:
            entries_temp = [("<unknown>", e) for e in entries]

        for key, entry in entries_temp:
            if not isinstance(entry, dict):
                continue

            match = True
            for prop_name, expr in conditions:
                prop_match = False
                for prop, value in entry.items():
                    val = str(value)
                    if prop != prop_name:
                        continue
                    if regex.match(expr, str(val)):
                        prop_match = True
                        break
                if not prop_match:
                    match = False
                    break

            if not match:
                continue

            any_found = True

            if arg.list:
                yield f"{key:50} ({cat})"
            elif arg.keys:
                yield f"----- Category {cat}: {key} -----"
                _check_is_dict(entry, f"{cat} --> {key}")

                keys = list(entry.keys())
                keys.sort()
                yield keys
            else:
                yield f"----- Category {cat}: {key} -----"
                yield json.dumps(entry, indent=4)

    if not any_found:
        yield f"No data found for pairs {arg.values}"


def _check_is_dict(entry, search_str):
    if not isinstance(entry, dict):
        raise ValueError(f"Not a dictionary at data -> {search_str}")
