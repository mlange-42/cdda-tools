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

    if copy:
        _copy_to_data(copy_data, data)

    return data


def _copy_to_data(copy_data, data):
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches

    total_to_copy = sum(len(v) for _, v in copy_data.items())

    while True:
        any_left = False
        any_found = False

        for type_id, type_data in copy_data.items():
            to_remove = []
            for entry_id, entry in type_data.items():
                from_id = entry["copy-from"]

                if from_id in data[type_id]:
                    new_entry = dict(data[type_id][from_id])
                elif from_id in data["GENERIC"]:
                    new_entry = dict(data["GENERIC"][from_id])
                else:
                    continue

                if "abstract" in new_entry:
                    del new_entry["abstract"]

                for key, value in entry.items():
                    new_entry[key] = value

                _add_to_data(data, new_entry)
                to_remove.append(entry_id)
                any_found = True

            for entry_id in to_remove:
                del type_data[entry_id]

            if len(type_data) > 0:
                any_left = True

        if not any_left:
            break

        if not any_found:
            remaining = sum(len(v) for _, v in copy_data.items())
            print(
                f"Warning: not all inheriting entries could be resolved "
                f"({remaining}/{total_to_copy} remaining)"
            )

            for type_id, type_data in copy_data.items():
                for _entry_id, entry in type_data.items():
                    _add_to_data(data, entry)

            break


def _add_to_data_or_copy(data, copy_data, entry, types, copy):
    entry_type = entry["type"]
    if types is not None and entry_type not in types:
        return

    if copy and "copy-from" in entry:
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
