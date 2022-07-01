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
