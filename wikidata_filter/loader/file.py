import json

from wikidata_filter.loader.base import DataProvider
from wikidata_filter.util.file_loader import open_file


class FileLoader(DataProvider):
    """
    文件加载器
    """
    hold: bool = False
    instream = None

    def close(self):
        if self.hold and self.instream:
            self.instream.close()


class LineBasedFileLoader(FileLoader):
    """
    基于行的文件加载器
    """
    def __init__(self, encoding="utf8"):
        super().__init__()
        self.encoding = encoding

    def iter(self):
        for line in self.instream:
            yield line.decode(self.encoding)


class CompressFileLoader(FileLoader):
    def __init__(self, input_file, mode='rb'):
        super().__init__()
        self.instream = open_file(input_file, mode)


class JsonLineFileLoader(LineBasedFileLoader):
    """
     Json行文件
    """
    def __init__(self, input_file, encoding="utf8"):
        super().__init__(encoding=encoding)
        if isinstance(input_file, str):
            self.instream = open_file(input_file, mode='rb')
            self.hold = True
        else:
            self.instream = input_file

    def iter(self):
        for line in super().iter():
            yield json.loads(line)


class JsonLoader(FileLoader):
    def __init__(self, input_file, encoding="utf8"):
        super().__init__()
        if isinstance(input_file, str):
            self.instream = open_file(input_file, mode='rb')
            self.hold = True
        else:
            self.instream = input_file
        self.encoding = encoding

    def iter(self):
        content = self.instream.read().decode(self.encoding)
        row = json.loads(content)
        yield row


class JsonArrayLoader(FileLoader):
    """
    整个文件作为JsonArray
    """
    def __init__(self, input_file, encoding="utf8"):
        super().__init__()
        if isinstance(input_file, str):
            self.instream = open_file(input_file, mode='rb')
            self.hold = True
        else:
            self.instream = input_file
        self.encoding = encoding

    def iter(self):
        content = self.instream.read().decode(self.encoding)
        json_array = json.loads(content)
        for item in json_array:
            yield item


class CSVLoader(LineBasedFileLoader):
    def __init__(self, input_file: str, sep: str = ',', header: bool = True, encoding='utf8'):
        super().__init__(encoding=encoding)
        self.header = header
        self.sep = sep
        self.instream = open_file(input_file, "rb")
        self.hold = True

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


class TxtLoader(LineBasedFileLoader):
    def __init__(self, input_file: str, encoding='utf8'):
        super().__init__(encoding=encoding)
        self.instream = open_file(input_file, "rb")


class DirectoryLoader(DataProvider):
    def __init__(self, directory_path: str, suffix: str = None):
        self.path = directory_path
        self.suffix = suffix

