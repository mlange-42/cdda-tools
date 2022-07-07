"""Show game data."""
import argparse
from fnmatch import translate

import regex

from .. import game
from . import Command

PATH_SEPARATOR = "/"


class Table(Command):
    """Show game data."""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "table",
            help="Show JSON game data in tables.",
            description="Show JSON game data in tables.\n\n"
            "Examples:\n\n"
            "  cdda_tools table TOOL/rapier TOOL/sword_bayonet TOOL/sword_xiphos "
            "--columns name/str bashing cutting piercing weight volume techniques",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser.add_argument(
            "paths",
            type=str,
            nargs="+",
            help=f"two-element item paths, with path elements delimited by '{PATH_SEPARATOR}' "
            f"(<type>/<id blob>)",
        )

        parser.add_argument(
            "--columns",
            "-c",
            type=str,
            nargs="+",
            required=True,
            help=f"columns/property paths to tabulate; path separator is '{PATH_SEPARATOR}'",
        )

    def exec(self, arg):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-nested-blocks
        data = game.read_game_data(arg.dir)

        columns = ["id"] + arg.columns
        column_paths = [col.split(PATH_SEPARATOR) for col in columns]
        width = {c: 3 for c in columns}

        table_data = []

        for path in arg.paths:
            path_elem = path.split(PATH_SEPARATOR)
            if len(path_elem) != 2:
                raise ValueError(
                    f"Only two-element paths are allowed. "
                    f"Path '{path}' has {len(path_elem)} element(s)"
                )
            type_cat = path_elem[0]
            id_blob = path_elem[1]

            if type_cat not in data:
                raise ValueError(f"Type '{type_cat}' not found in game data.")

            reg = regex.compile(translate(id_blob))
            entries = data[type_cat]

            for key, entry in entries.items():
                if not regex.match(reg, key):
                    continue

                data_entry = {}
                for col, col_path in zip(columns, column_paths):
                    curr_entry = entry
                    for col_path_part in col_path:
                        if isinstance(curr_entry, dict):
                            if col_path_part in curr_entry:
                                curr_entry = curr_entry[col_path_part]
                            else:
                                curr_entry = "-"
                                break
                        elif isinstance(curr_entry, list):
                            index = int(col_path_part)
                            curr_entry = (
                                curr_entry[index] if index < len(curr_entry) else "?"
                            )
                        else:
                            curr_entry = "-"
                            break

                    data_entry[col] = str(curr_entry)

                data_entry["id"] = key

                table_data.append(data_entry)

        for entry in table_data:
            for col in columns:
                str_len = len(entry[col])
                if str_len > width[col]:
                    width[col] = str_len

        yield " | ".join(
            [
                "{val:>{width}}".format(val=col[0 : width[col]], width=width[col])
                for col in columns
            ]
        )
        for entry in table_data:
            line = " | ".join(
                [
                    "{val:>{width}}".format(val=entry[col], width=width[col])
                    for col in columns
                ]
            )
            yield line
