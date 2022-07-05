"""
Cataclysm DDA Python tools, CLI functions.
"""
import argparse

from . import commands

COMMANDS = {
    "copy-player": commands.CopyPlayer(),
    "copy-vehicle": commands.CopyVehicle(),
    "note": commands.Note(),
    "notes": commands.Notes(),
    "find": commands.Find(),
    "list": commands.List(),
    "show-data": commands.ShowData(),
    "vehicle-mod": commands.VehicleMod(),
}


def run_cli(args):
    """Run the CLI with parsed arguments (see parse_args(args))"""
    if args.subparser not in COMMANDS:
        raise ValueError("Unknown sub-command '{}'.".format(args.subparser))

    COMMANDS[args.subparser].exec(args)


def parse_args(args=None):
    """Parse arguments array"""
    parser = _create_parser()
    return parser.parse_args(args)


def _create_parser():
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        description="Cataclysm DDA Python tools.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default=".",
        help="game directory, default '.'",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="debug mode, prints full error stack traces",
    )

    subparsers = parser.add_subparsers(
        help="Sub-commands",
        dest="subparser",
    )

    for _, cmd in COMMANDS.items():
        cmd.add_subcommand(subparsers)

    return parser
