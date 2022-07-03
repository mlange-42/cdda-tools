import argparse

from . import commands

COMMANDS = {
    "copy-player": commands.CopyPlayer(),
    "copy-vehicle": commands.CopyVehicle(),
    "note": commands.Note(),
    "notes": commands.Notes(),
    "find": commands.Find(),
    "vehicle-mod": commands.VehicleMod(),
}


def create_parser():
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

    for name, cmd in COMMANDS.items():
        cmd.add_subcommand(subparsers)

    return parser


def parse_args(args=None):
    parser = create_parser()
    return parser.parse_args(args)


if __name__ == "__main__":
    arg = parse_args()

    if arg.subparser not in COMMANDS.keys():
        print("Unknown sub-command '{}'.".format(arg.subparser))
        exit(1)

    COMMANDS[arg.subparser].exec(arg)
