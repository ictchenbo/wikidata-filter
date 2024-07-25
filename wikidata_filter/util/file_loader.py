import json


def get_lines(file):
    with open(file, "r") as fin:
        for line in fin:
            yield line.strip()


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


def load_data_dict(dict_json_path: str):
    with open(dict_json_path, encoding='utf8') as fin:
        root = json.load(fin)
        return {
            val["id"]: val for val in root["values"]
        }
