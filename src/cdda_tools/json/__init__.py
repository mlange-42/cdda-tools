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


def write_json(data, path):
    f = open(path, "w")
    json.dump(data, f)
    f.close()
