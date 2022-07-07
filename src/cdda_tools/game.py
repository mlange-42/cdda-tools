"""CDDA game data"""
import glob
from os import path

import regex

from . import json_utils

DATA_DIR = "data"
JSON_DIR = "json"

NON_NUMBER_REGEX = regex.compile("[^.\\-0-9]+")


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
                    orig_entry = data[type_id][from_id]
                elif from_id in data["GENERIC"]:
                    orig_entry = data["GENERIC"][from_id]
                else:
                    continue

                if "copy-from" in orig_entry:
                    continue

                new_entry = dict(orig_entry)
                if "abstract" in new_entry:
                    del new_entry["abstract"]

                for key, value in entry.items():
                    _overwrite_property(new_entry, key, value)

                if "copy-from" in new_entry:
                    del new_entry["copy-from"]

                _adjust_inheritance(new_entry)

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


def _overwrite_property(new_entry, key, value):
    if key not in new_entry:
        new_entry[key] = value
    elif isinstance(value, dict):
        if isinstance(new_entry[key], dict):
            for sub_key, sub_value in value.items():
                _overwrite_property(new_entry[key], sub_key, sub_value)
        else:
            new_entry[key] = value
    else:
        new_entry[key] = value


def _adjust_inheritance(entry):
    if "proportional" in entry:
        _adjust_inheritance_func(entry, "proportional", lambda a, b: round(a * b, 1))
        del entry["proportional"]

    if "relative" in entry:
        _adjust_inheritance_func(entry, "relative", lambda a, b: round(a + b, 1))
        del entry["relative"]


def _adjust_inheritance_func(entry, prop, func):
    # pylint: disable=too-many-branches
    for key, factor in entry[prop].items():
        if key not in entry:
            continue

        factor = factor.split(" ") if isinstance(factor, str) else [factor]
        if isinstance(factor[0], str):
            factor[0] = float(factor[0])

        old_value = entry[key]
        if isinstance(old_value, (int, float)):
            entry[key] = func(old_value, factor[0])
        elif isinstance(old_value, str):
            if " " in old_value:
                parts = old_value.split(" ")
            else:
                unit = regex.findall(NON_NUMBER_REGEX, old_value)[0]
                parts = [old_value.replace(unit, ""), unit]

            if len(factor) > 1 and factor[1] != parts[1]:
                print(
                    f"Warning: inheritance adjustment not possible due to different units "
                    f"({parts[1]}, {factor[1]})"
                )
            else:
                entry[key] = f"{func(float(parts[0]), factor[0])} {parts[1]}"

        elif isinstance(old_value, list):
            # pylint: disable=fixme
            # TODO
            pass
        else:
            for sub_key, sub_factor in factor[0].items():
                if sub_key in old_value and (isinstance(sub_factor, (int, float))):
                    entry[key][sub_key] = func(old_value[sub_key], sub_factor)


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
