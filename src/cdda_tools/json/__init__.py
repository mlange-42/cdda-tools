"""
JSON file handling.
"""
import json


def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data
