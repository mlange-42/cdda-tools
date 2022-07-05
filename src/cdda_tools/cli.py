"""
Cataclysm DDA Python tools, CLI functions.
"""
import argparse
import sys

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


def run_cli(args=None):
    """Run the CLI with given arguments array"""
    arg = parse_args(args)

    if arg.subparser not in COMMANDS:
        print("Unknown sub-command '{}'.".format(arg.subparser))
        sys.exit(1)

    COMMANDS[arg.subparser].exec(arg)


def create_parser():
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

    subparsers = parser.add_subparsers(
        help="Sub-commands",
        dest="subparser",
    )

    for _, cmd in COMMANDS.items():
        cmd.add_subcommand(subparsers)

    return parser


def parse_args(args=None):
    """Parse arguments"""
    parser = create_parser()
    return parser.parse_args(args)
