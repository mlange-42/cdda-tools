"""CDDA game data"""
import glob
from os import path

from . import json_utils

DATA_DIR = "data"
JSON_DIR = "json"


def read_game_data(game_dir, types=None):
    """Read all CDDA json into a large nested dictionary"""
    # pylint: disable=too-many-branches

    json_glob = path.join(game_dir, DATA_DIR, JSON_DIR, "**", "*.json")

    if types is not None:
        types = set(types)

    data = {}

    for file in glob.iglob(json_glob, recursive=True):
        json_data = json_utils.read_json(file)
        for entry in json_data:
            entry_type = entry["type"]
            if types is not None and entry_type not in types:
                continue
            if "id" in entry:
                entry_ids = entry["id"]
                if not isinstance(entry_ids, list):
                    entry_ids = [entry_ids]
                for entry_id in entry_ids:
                    if entry_type in data:
                        data[entry_type][entry_id] = entry
                    else:
                        data[entry_type] = {entry_id: entry}
            elif (
                "abstract" in entry
                and entry_type != "recipe"
                and entry_type != "uncraft"
            ):
                entry_id = entry["abstract"]
                if entry_type in data:
                    data[entry_type][entry_id] = entry
                else:
                    data[entry_type] = {entry_id: entry}
            else:
                if entry_type in data:
                    data[entry_type].append(entry)
                else:
                    data[entry_type] = [entry]

    return data
