"""
JSON file handling.
"""
import json


def read_json(path):
    f = open(path)
    lines = f.readlines()
    if lines[0].startswith("#"):
        lines = lines[1:]
    data = json.loads("".join(lines))
    f.close()
    return data


def write_json(data, path, pretty=False):
    f = open(path, "w")

    if pretty:
        json.dump(data, f, indent=4)
    else:
        json.dump(data, f)

    f.close()
