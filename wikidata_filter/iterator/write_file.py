import json
from wikidata_filter.iterator.base import JsonIterator


class WriteFile(JsonIterator):
    """
        输出数据到文件
    """
    def __init__(self, output_file: str, append: bool = False, encoding: str = None):
        super().__init__()
        self.writer = open(output_file, 'a' if append else 'w', encoding=encoding)

    def on_complete(self):
        self.writer.close()


class WriteJson(WriteFile):
    """
    写JSON文件
    """
    def __init__(self, output_file: str, append: bool = False, encoding: str = None):
        super().__init__(output_file, append=append, encoding=encoding)

    def on_data(self, item: dict or None, *args):
        self.writer.write(json.dumps(item, ensure_ascii=False))
        self.writer.write('\n')
        return item


class WriteCSV(WriteFile):
    """
    写CSV文件
    """
    def __init__(self, output_file: str, keys: list = None, seperator=',', append: bool = False, encoding: str = None):
        super().__init__(output_file, append=append, encoding=encoding)
        self.keys = keys
        self.seperator = seperator

    def on_data(self, item: dict or None, *args):
        if self.keys is None:
            for k, v in item.items():
                self.writer.write(str(v))
                self.writer.write(self.seperator)
        else:
            for k in self.keys:
                self.writer.write(str(item.get(k)))
                self.writer.write(self.seperator)
        self.writer.write('\n')
        return item

