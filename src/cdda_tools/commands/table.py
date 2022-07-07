"""Show game data."""
import argparse
from fnmatch import translate

import regex

from .. import game
from . import Command, util

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
            f"(<type>/<id glob>)",
        )

        parser.add_argument(
            "--columns",
            "-c",
            type=str,
            nargs="+",
            required=True,
            help=f"columns/property paths to tabulate; path separator is '{PATH_SEPARATOR}'",
        )

        util.add_no_inheritance_options(parser)

        parser.add_argument(
            "--format",
            "-f",
            type=str,
            help="output format if other than print for direct viewing. one of [md html csv]",
        )

    def exec(self, arg):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-nested-blocks
        data = game.read_game_data(arg.dir, copy=not arg.no_inherit)

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
            id_glob = path_elem[1]

            if type_cat not in data:
                raise ValueError(f"Type '{type_cat}' not found in game data.")

            reg = regex.compile(translate(id_glob))
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

        if arg.format is None:
            yield from _print_table_simple(table_data, columns, width)
        elif arg.format == "html":
            yield from _print_table_html(table_data, columns, width)
        elif arg.format == "md":
            yield from _print_table_markdown(table_data, columns, width)
        elif arg.format == "csv":
            yield from _print_table_csv(table_data, columns, width)
        else:
            raise ValueError(
                f"Unrecognized argument '{arg.format}' for option --format. "
                f"Must be one of [html md csv]."
            )


def _print_table_simple(table_data, columns, widths):
    yield " | ".join(
        [
            "{val:>{width}}".format(val=col[0 : widths[col]], width=widths[col])
            for col in columns
        ]
    )
    for entry in table_data:
        yield " | ".join(
            [
                "{val:>{width}}".format(val=entry[col], width=widths[col])
                for col in columns
            ]
        )


def _print_table_markdown(table_data, columns, widths):
    yield "| " + " | ".join(
        [
            "{val:>{width}}".format(val=col[0 : widths[col]], width=widths[col])
            for col in columns
        ]
    ) + " |"
    yield "| " + " | ".join(["-" * widths[col] for col in columns]) + " |"
    for entry in table_data:
        yield "| " + " | ".join(
            [
                "{val:>{width}}".format(val=entry[col], width=widths[col])
                for col in columns
            ]
        ) + " |"


def _print_table_html(table_data, columns, widths):
    yield "<table>"
    yield "<tr>\n    <th>" + "</th>\n    <th>".join(
        ["{val}".format(val=col[0 : widths[col]]) for col in columns]
    ) + "</th>\n</tr>"

    for entry in table_data:
        yield "<tr>\n    <td>" + "</td>\n    <td>".join(
            ["{val}".format(val=entry[col]) for col in columns]
        ) + "</td>\n</tr>"
    yield "</table>"


def _print_table_csv(table_data, columns, _widths):
    yield ";".join(columns)
    for entry in table_data:
        yield ";".join(["{}".format(entry[col]) for col in columns])
