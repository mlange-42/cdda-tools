from os import path
import glob
from .. import json

SAVE_DIR = "save"


def get_world_path(directory, world):
    world_dir = path.join(directory, SAVE_DIR, world)
    if not path.isdir(world_dir):
        print("World directory {} does not exist.".format(world_dir))
        exit(1)

    return world_dir


def get_save_path(world_dir, player):

    sav_files = glob.glob(path.join(world_dir, "*.sav"))
    if not sav_files:
        print("No saved characters found in world directory {}.".format(world_dir))
        exit(1)

    players = []

    for sav in sav_files:
        character_data = json.read_json(sav, skip_lines=1)
        players.append(character_data["player"]["name"])

    if len(players) > 1 and player is None:
        print(
            "Multiple players in world directory {}. Requires option --player/-p.".format(
                world_dir
            )
        )
        exit(1)

    if player not in players:
        print(
            "Player '{}' not found in world directory {}. Found {}.".format(
                player, world_dir, ", ".join(players)
            )
        )
        exit(1)

    pl = players[0] if player is None else player
    pos = players.index(pl)

    return sav_files[pos][:-4], pl
