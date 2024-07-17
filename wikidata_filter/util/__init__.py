import json
from .file_loader import get_lines


def SetFromCSV(file, index=0):
    s = set()
    for line in get_lines(file):
        if "," in line:
            s.add(line.split(",")[index])
    return s


def SetFromJSON(file, key_key='id'):
    s = set()
    for line in get_lines(file):
        row = json.loads(line)
        if key_key in row:
            s.add(row[key_key])
    return s


def KVFromCSV(file, key_col=0, val_col=1, sep=","):
    kv = {}
    for line in get_lines(file):
        if sep in line:
            parts = line.split(sep)
            kv[parts[key_col].strip()] = parts[val_col]
    return kv


def KVFromJSON(file, key_key='id', val_key='name'):
    kv = {}
    for line in get_lines(file):
        row = json.loads(line)
        if key_key in row and val_key in row:
            kv[row[key_key]] = row[val_key]
    return kv


