import json

from wikidata_filter.loader.base import DataProvider
from wikidata_filter.util.file_loader import open_file


class FileLoader(DataProvider):
    """
    文件加载器
    """
    hold: bool = False
    instream = None
    filename: str = None

    def close(self):
        if self.hold and self.instream:
            self.instream.close()

    def __str__(self):
        return f"{self.name}('{self.filename}')"


class Text(FileLoader):
    """基于行的文本文件加载器"""
    def __init__(self, input_file: str, encoding='utf8'):
        self.encoding = encoding
        self.instream = open_file(input_file, "rb")
        self.hold = True
        self.filename = input_file

    def iter(self):
        for line in self.instream:
            yield line.decode(self.encoding)


class JsonLine(Text):
    """
     Json行文件
    """
    def __init__(self, input_file, encoding="utf8"):
        super().__init__(input_file, encoding=encoding)

    def iter(self):
        for line in super().iter():
            yield json.loads(line)


class JsonArray(Text):
    """
    整个文件作为JsonArray
    """
    def __init__(self, input_file, encoding="utf8"):
        super().__init__(input_file, encoding)

    def iter(self):
        content = self.instream.read().decode(self.encoding)
        json_array = json.loads(content)
        for item in json_array:
            yield item


class Json(Text):
    """整个文件作为一个JSON对象（不管是dict还是list）"""
    def __init__(self, input_file, encoding="utf8"):
        super().__init__(input_file, encoding)

    def iter(self):
        content = self.instream.read().decode(self.encoding)
        row = json.loads(content)
        yield row


class JsonFree(Text):
    """对格式化JSON文件进行加载 自动检测边界"""
    def __init__(self, input_file, encoding="utf8"):
        super().__init__(input_file, encoding)

    def iter(self):
        lines = []
        for line in super().iter():
            line_s = line.rstrip()
            if lines:
                lines.append(line_s)
                # 遇到]或}行 认为是JSON对象或JSON数组的结束
                if line_s == ']' or line_s == '}':
                    one = json.loads(''.join(lines))
                    yield one
                    lines.clear()
            else:
                if not line_s:
                    continue
                lines.append(line_s)


class CSV(Text):
    """读取CSV文件 每行作为一个对象传输"""
    def __init__(self, input_file: str, sep: str = ',', header: bool = True, encoding='utf8'):
        super().__init__(input_file, encoding=encoding)
        self.header = header
        self.sep = sep

    def iter(self):
        try:
            import csv
        except ImportError:
            raise Exception("failed to import csv")
        reader = csv.reader(super().iter())
        header = None
        for index, row in enumerate(reader):
            if self.header:
                if index == 0:
                    header = row
                else:
                    yield dict(zip(header, row))
            else:
                yield row


class Directory(DataProvider):
    """扫描文件夹 对指定后缀的文件按照默认参数进行读取"""
    def __init__(self, directory_path: str, *suffix, recursive: bool = False):
        """
        :param directory_path 指定文件夹路径
        :param *suffix 文件的后缀
        :param recursive 是否递归遍历文件夹
        """
        self.path = directory_path
        self.suffix = suffix
        self.recursive = recursive
