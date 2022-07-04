"""
JSON file handling.
"""
import json


def read_json(path):
    """Read JSON file to dictionary."""
    f = open(path)
    lines = f.readlines()
    if lines[0].startswith("#"):
        lines = lines[1:]
    data = json.loads("".join(lines))
    f.close()
    return data


def write_json(data, path, pretty=False):
    """Write dictionary to JSON file."""
    f = open(path, "w")

    if pretty:
        json.dump(data, f, indent=4)
    else:
        json.dump(data, f)

    f.close()
