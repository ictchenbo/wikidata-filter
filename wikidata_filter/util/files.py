"""文件辅助工具 方便流程使用"""


def read_text(filename: str, encoding="utf8"):
    """读取文本文件"""
    with open(filename, encoding=encoding) as fin:
        return fin.read()


def read_json(filename: str, encoding="utf8"):
    """读取JSON"""
    import json
    with open(filename, encoding=encoding) as fin:
        return json.load(fin)

