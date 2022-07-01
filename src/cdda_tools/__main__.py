from os import path
import argparse
import glob

from . import json

SAVE_DIR = "save"


def create_parser():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--dir", "-d",
        type=str,
        default=".",
        help="game directory, default '.'",
    )
    parser.add_argument(
        "--world", "-w",
        type=str,
        required=True,
        help="the game world",
    )
    parser.add_argument(
        "--player", "-p",
        type=str,
        help="the player, optional if only one player in world",
    )

    return parser


def parse_args(args=None):
    parser = create_parser()
    return parser.parse_args(args)


def get_save(arg):
    world_dir = path.join(arg.dir, SAVE_DIR, arg.world)
    if not path.isdir(world_dir):
        print("World directory {} does not exist.".format(world_dir))
        exit(1)

    sav_files = glob.glob(path.join(world_dir, "*.sav"))
    if not sav_files:
        print("No saved characters found in world directory {}.".format(world_dir))
        exit(1)

    players = []

    for sav in sav_files:
        character_data = json.read_json(sav, skip_lines=1)
        players.append(character_data["player"]["name"])

    if len(players) > 1 and arg.player is None:
        print("Multiple players in world directory {}. Requires option --player/-p.".format(world_dir))
        exit(1)

    if arg.player not in players:
        print("Player '{}' not found in world directory {}. Found {}.".format(arg.player, world_dir, ", ".join(players)))
        exit(1)

    player = players[0] if arg.player is None else arg.player
    pos = players.index(player)

    return world_dir, sav_files[pos][:-4], player


if __name__ == "__main__":
    arg = parse_args()
    world, save, player = get_save(arg)
    print(world, save, player)
