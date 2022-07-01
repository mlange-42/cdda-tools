"""
JSON file handling.
"""
import json


def read_json(path, skip_lines=0):
    f = open(path)
    lines = f.readlines()[skip_lines:]
    data = json.loads("".join(lines))
    f.close()
    return data


def write_json(data, path):
    f = open(path, "w")
    json.dump(data, f, indent=4)
    f.close()
