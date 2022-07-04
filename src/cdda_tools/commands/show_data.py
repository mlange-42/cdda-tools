"""Show game data."""
import argparse
import json
import sys
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

        parser.add_argument(
            "ids",
            type=str,
            nargs="*",
            help="keys to print data for (category id [property...]), "
            "or ID glob patterns to search for when using --search",
        )
        parser.add_argument(
            "--keys",
            "-k",
            action="store_true",
            help="print only keys, not the complete data",
        )
        parser.add_argument(
            "--search",
            "-s",
            action="store_true",
            help="search for IDs, instead of using the query hierarchically",
        )
        parser.add_argument(
            "--list",
            "-l",
            action="store_true",
            help="when used with --search, only list matches",
        )

    def exec(self, arg):
        if arg.search:
            _search(arg)
        else:
            _hierarchical(arg)


def _hierarchical(arg):
    if arg.list:
        print("Argument --list can only be used with --search.")
        sys.exit(1)

    data = game.read_game_data(arg.dir)
    extract = data
    search_str = "data"

    if arg.ids is not None:
        for key in arg.ids:
            _check_is_dict(extract, search_str)

            if key in extract:
                extract = extract[key]
            else:
                print(f"Id {key} not found in {search_str}")
                sys.exit(1)
            search_str += f" --> {key}"

    if arg.keys:
        _check_is_dict(extract, search_str)

        keys = list(extract.keys())
        keys.sort()
        print(keys)
    else:
        print(json.dumps(extract, indent=4))


def _search(arg):
    if arg.list and arg.keys:
        print("Arguments --list and --keys are mutually exclusive.")
        sys.exit(1)

    data = game.read_game_data(arg.dir)

    rex = [regex.compile(translate(pat)) for pat in arg.ids]
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
                        print(f"{key:50} ({cat})")
                    elif arg.keys:
                        print(f"----- Category {cat}: {key} -----")
                        _check_is_dict(entry, f"{cat} --> {key}")

                        keys = list(entry.keys())
                        keys.sort()
                        print(keys)
                    else:
                        print(f"----- Category {cat}: {key} -----")
                        print(json.dumps(entry, indent=4))
    if not any_found:
        print(f"No data found for globs {arg.ids}")


def _check_is_dict(entry, search_str):
    if not isinstance(entry, dict):
        print(f"Not a dictionary at data -> {search_str}")
        sys.exit(1)
