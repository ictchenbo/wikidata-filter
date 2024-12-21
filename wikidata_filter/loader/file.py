import os
from wikidata_filter.loader.base import DataProvider
from wikidata_filter.util.files import open_file


class File(DataProvider):
    """
    文件加载器
    """
    instream = None
    filename: str = None

    def close(self):
        if self.instream:
            self.instream.close()
            self.instream = None

    def __str__(self):
        return f"{self.name}('{self.filename}')"


class BinaryFile(File):
    def __init__(self, input_file: str, auto_open: bool = True, **kwargs):
        assert os.path.exists(input_file) and os.path.isfile(input_file), f"文件不存在或不是文件: {input_file}"
        if auto_open:
            self.instream = open_file(input_file, "rb")
        self.filename = input_file
