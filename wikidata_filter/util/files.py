import json as JSON


def text(filename: str, encoding="utf8"):
    """读取文本文件"""
    with open(filename, encoding=encoding) as fin:
        return fin.read()


def json(filename: str, encoding="utf8"):
    """读取JSON"""
    with open(filename, encoding=encoding) as fin:
        return JSON.load(fin)


def get_lines(filename: str, encoding="utf8"):
    with open(filename, "r", encoding=encoding) as fin:
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
