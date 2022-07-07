"""CDDA game data"""
import glob
from os import path

from . import json_utils

DATA_DIR = "data"
JSON_DIR = "json"


def read_game_data(game_dir, types=None, copy=False):
    """Read all CDDA json into a large nested dictionary"""
    json_glob = path.join(game_dir, DATA_DIR, JSON_DIR, "**", "*.json")

    if types is not None:
        types = set(types)

    data = {}
    copy_data = {}

    for file in glob.iglob(json_glob, recursive=True):
        json_data = json_utils.read_json(file)
        for entry in json_data:
            _add_to_data_or_copy(data, copy_data, entry, types, copy)

    return data


def _add_to_data_or_copy(data, copy_data, entry, types, copy):
    entry_type = entry["type"]
    if types is not None and entry_type not in types:
        return

    if copy and "copy-from" in entry:
        from_id = entry["copy-from"]
        if entry_type in data and from_id in data[entry_type]:
            new_entry = dict(data[entry_type][from_id])
            for key, value in entry:
                new_entry[key] = value
            _add_to_data(data, new_entry)
        else:
            _add_to_data(copy_data, entry)
    else:
        _add_to_data(data, entry)


def _add_to_data(data, entry):
    entry_type = entry["type"]
    if "id" in entry:
        entry_ids = entry["id"]
        if not isinstance(entry_ids, list):
            entry_ids = [entry_ids]
        for entry_id in entry_ids:
            if entry_type in data:
                data[entry_type][entry_id] = entry
            else:
                data[entry_type] = {entry_id: entry}
    elif "abstract" in entry:
        entry_id = entry["abstract"]
        if entry_type in data:
            data[entry_type][entry_id] = entry
        else:
            data[entry_type] = {entry_id: entry}
    else:
        if entry_type in data:
            data[entry_type][str(len(data[entry_type]))] = entry
        else:
            data[entry_type] = {"0": entry}
