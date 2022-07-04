"""
JSON file handling.
"""
import json


def read_json(path):
    """Read JSON file to dictionary."""
    with open(path, encoding="utf-8") as file:
        lines = file.readlines()
        if lines[0].startswith("#"):
            lines = lines[1:]
        data = json.loads("".join(lines))
    return data


def write_json(data, path, pretty=False):
    """Write dictionary to JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        if pretty:
            json.dump(data, file, indent=4)
        else:
            json.dump(data, file)
