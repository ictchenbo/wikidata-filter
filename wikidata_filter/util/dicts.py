import json
from .files import get_lines


def from_csv(file, key_col=0, val_col=1, sep=",", encoding="utf8"):
    kv = {}
    for line in get_lines(file, encoding=encoding):
        if sep in line:
            parts = line.split(sep)
            kv[parts[key_col].strip()] = parts[val_col]
    return kv


def from_json(file, key_key='id', val_key='name', encoding="utf8"):
    kv = {}
    for line in get_lines(file, encoding=encoding):
        row = json.loads(line)
        if key_key in row and val_key in row:
            kv[row[key_key]] = row[val_key]
    return kv
