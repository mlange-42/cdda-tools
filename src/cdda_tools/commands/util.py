from os import path
import glob
from .. import json

SAVE_DIR = "save"
MAPS_DIR = "maps"

OVERMAP_SIZE = 180
MAP_SIZE = 24
SUBMAP_SIZE = 12


def get_world_path(directory: str, world: str) -> str:
    world_dir = path.join(directory, SAVE_DIR, world)
    if not path.isdir(world_dir):
        print("World directory {} does not exist.".format(world_dir))
        exit(1)

    return world_dir


def get_save_path(world_dir: str, player: str) -> (str, str, str):
    sav_files = glob.glob(path.join(world_dir, "*.sav"))
    if not sav_files:
        print("No saved characters found in world directory {}.".format(world_dir))
        exit(1)

    players = []

    for sav in sav_files:
        character_data = json.read_json(sav)
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

    save_name = sav_files[pos][len(world_dir) + 1 : -4]

    return sav_files[pos], save_name, pl


def file_contains(p: str, text: str) -> bool:
    file = open(p, "r")
    content = file.read()
    cont = text in content
    file.close()
    return cont


def read_file(p: str) -> str:
    file = open(p, "r")
    content = file.read()
    file.close()
    return content


def index_to_xy_overmap(idx):
    x = idx % OVERMAP_SIZE
    y = idx // OVERMAP_SIZE
    return x, y


