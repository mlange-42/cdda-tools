import argparse

from . import commands

COMMANDS = {"copy-player": commands.CopyPlayer()}


def create_parser():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default=".",
        help="game directory, default '.'",
    )

    subparsers = parser.add_subparsers(help="sub-command help", dest="subparser")
    parser_copy_player = subparsers.add_parser("copy-player", help="copy-player help")

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
        help="the player to copy from, optional if only one player in world",
    )

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
