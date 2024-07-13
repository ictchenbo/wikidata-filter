import json


def get_lines(file):
    with open(file, "r") as fin:
        for line in fin:
            yield line.strip()


def get_lines_part(file, index=0):
    s = set()
    for line in get_lines(file):
        if "," in line:
            s.add(line.split(",")[index])
    return s


def kv_from_csv(file, key_col=0, val_col=1, sep=","):
    kv = {}
    for line in get_lines(file):
        if sep in line:
            parts = line.split(sep)
            kv[parts[key_col].strip()] = parts[val_col]
    return kv


def kv_from_json(file, key_key='id', val_key='name'):
    kv = {}
    for line in get_lines(file):
        row = json.loads(line)
        if key_key in row and val_key in row:
            kv[row[key_key]] = row[val_key]
    return kv


def key_from_json(file, key_key='id'):
    s = set()
    for line in get_lines(file):
        row = json.loads(line)
        if key_key in row:
            s.add(row[key_key])
    return s


def open_file(filename: str, mode="rb"):
    if filename.endswith('.bz2'):
        import bz2
        stream = bz2.open(filename, mode)
    elif filename.endswith('.gz'):
        import gzip
        stream = gzip.open(filename, mode)
    else:
        stream = open(filename, mode)
    return stream


def display_file_content(filename: str, encoding="utf8", limit=1000):
    with open_file(filename) as fin:
        for line in fin:
            print(line.decode(encoding))
            limit -= 1
            if limit <= 0:
                break
