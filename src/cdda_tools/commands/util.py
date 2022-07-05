"""Utility functions for CLI commands"""
import glob
import math
import os
from os import path

from .. import json_utils as json

SAVE_DIR = "save"
MAPS_DIR = "maps"

OVERMAP_SIZE = 180
MAP_SIZE = 24
SUBMAP_SIZE = 12
MAP_CHUNK_SIZE = 32


def add_world_option(parser, help_text):
    """Adds default --world option to a parser"""
    parser.add_argument(
        "--world",
        "-w",
        type=str,
        required=True,
        help=help_text,
    )


def add_world2_option(parser, help_text):
    """Adds default --world2 option to a parser"""
    parser.add_argument(
        "--world2",
        "-w2",
        type=str,
        required=True,
        help=help_text,
    )


def add_vehicle_option(parser, help_text):
    """Adds default --world option to a parser"""
    parser.add_argument(
        "--vehicle",
        "-v",
        type=str,
        required=True,
        help=help_text,
    )


def add_xy_options(parser):
    """Adds default x y option to a parser"""
    parser.add_argument(
        "x",
        type=str,
        help="x coordinate in overmap format -1'179 "
        '(quote neg. numbers, with a space: " -1\'32")',
    )
    parser.add_argument(
        "y",
        type=str,
        help="y coordinate in overmap format -1'179 "
        '(quote neg. numbers, with a space: " -1\'32")',
    )


def add_z_level_options(parser):
    """Adds default z level option to a parser"""
    parser.add_argument(
        "--z-levels",
        "-z",
        type=int,
        nargs="+",
        default=list(range(-10, 10)),
        help="a list of z-levels to process, default: all [-10, 10]",
    )


def add_dry_run_options(parser):
    """Adds default dry run option to a parser"""
    parser.add_argument(
        "--dry",
        action="store_true",
        help="dry-run (don't save changes)",
    )


def check_is_single_vehicle_source(source_maps, name):
    """
    Checks that only a single element is passed,
    and exits with vehicle-specific error message otherwise.
    """
    if len(source_maps) == 0:
        raise ValueError("Could not find source vehicle '{}'".format(name))
    if len(source_maps) > 1:
        raise ValueError(
            "Found multiple files for source vehicle name '{}'.\n"
            "Please rename the vehicle to something unique.".format(name)
        )


def check_levels(levels):
    """Checks that all z levels are in range [-10, 10]. Prints message and exits otherwise."""
    for level in levels:
        if level < -10 or level > 10:
            raise ValueError(
                "Unsupported z level: {}. Must be in range [-10, 10]".format(
                    level,
                )
            )


def get_world_path(directory: str, world: str) -> str:
    """Constructs and checks the world's save path"""
    world_dir = path.join(directory, SAVE_DIR, world)
    if not path.isdir(world_dir):
        raise ValueError("World directory {} does not exist.".format(world_dir))

    return world_dir


def get_save_path(world_dir: str, player: str) -> (str, str, str):
    """Get player save location: (.sav file path, file base name, player name)"""
    sav_files = glob.glob(path.join(world_dir, "*.sav"))
    if not sav_files:
        raise ValueError(
            "No saved characters found in world directory {}.".format(world_dir)
        )

    players = []

    for sav in sav_files:
        character_data = json.read_json(sav)
        players.append(character_data["player"]["name"])

    if len(players) > 1 and player is None:
        raise ValueError(
            "Multiple players in world directory {}. Requires option --player/-p.".format(
                world_dir
            )
        )

    if player is not None and player not in players:
        raise ValueError(
            "Player '{}' not found in world directory {}. Found {}.".format(
                player, world_dir, ", ".join(players)
            )
        )

    player_name = players[0] if player is None else player
    pos = players.index(player_name)

    save_name = sav_files[pos][len(world_dir) + 1 : -4]

    return sav_files[pos], save_name, player_name


def file_contains(file_path: str, text: str) -> bool:
    """Tests is a file's content contains given text"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        cont = text in content
    return cont


def read_file(file_path: str) -> str:
    """Read a text file"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def find_files_with_text(dir_path, text):
    """Collects all files with content containing text, recursively."""
    files = []
    for map_dir in os.walk(dir_path):
        for map_file in map_dir[2]:
            file_path = path.join(map_dir[0], map_file)
            if file_contains(file_path, text):
                files.append(file_path)
    return files


def index_to_xy_overmap(idx):
    """Converts the index of a flat 180x180 overmap array into relative overmap tile coors"""
    x_coord = idx % OVERMAP_SIZE
    y_coord = idx // OVERMAP_SIZE
    return x_coord, y_coord


def coord_to_map(x_major, x_minor, y_major, y_minor):
    """Converts overmap coords of format (1'123, -1'50) to absolute overmap tile coords"""
    return OVERMAP_SIZE * x_major + x_minor, OVERMAP_SIZE * y_major + y_minor


def map_to_chunk(x_coord, y_coord):
    """Converts absolute overmap tile coords to map chunk/directory coords"""
    x_chunk = x_coord / MAP_CHUNK_SIZE
    y_chunk = y_coord / MAP_CHUNK_SIZE

    x_chunk = int(math.floor(x_chunk))
    y_chunk = int(math.floor(y_chunk))

    return x_chunk, y_chunk


def note_to_str(note, omxy=None):
    """Formats a note for printing"""
    if omxy is None:
        omxy = ["?", "?"]
    return "{}{:3} | {}'{:3} {}'{:3} | {}".format(
        "!" if note[3] else " ",
        note[4] if note[3] else " ",
        omxy[0],
        note[0],
        omxy[1],
        note[1],
        note[2],
    )
