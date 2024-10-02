import io
from zipfile import ZipFile

from wikidata_filter.base import relative_path
from wikidata_filter.iterator.base import JsonIterator
from wikidata_filter.util.web_util import get_file
from wikidata_filter.util.file_loader import get_lines

config_base = "config/gdelt"


def parse_csv(url: str):
    if url.startswith("http://") or url.startswith("https://"):
        content = get_file(url)
        if len(content) < 100:
            return
        bytes_io = io.BytesIO(content)
        with ZipFile(bytes_io) as zipObj:
            filename = zipObj.filelist[0].filename
            with zipObj.open(filename) as f:
                for line in f:
                    line_s = line.decode("utf8").strip()
                    if line_s:
                        yield line_s.split('\t')
    else:
        with open(url, encoding="utf8") as fin:
            for line in fin:
                yield line.split('\t')


class SchemaBuilder:
    constructors = {}
    fields = []

    def __init__(self, filename: str):
        for line in get_lines(filename):
            if not line:
                continue
            field = line
            builder = str
            if ':' in line:
                pos = line.find(':')
                field = line[:pos]
                f_type = line[pos + 1:]
                if f_type.startswith('int'):
                    builder = int
                elif f_type.startswith('float'):
                    builder = float
            self.fields.append(field)
            self.constructors[field] = builder

    def init_value(self, field, val):
        if field not in self.constructors:
            return val
        builder = self.constructors[field]
        if val == '':
            if builder == int or builder == float:
                return None
        return builder(val)

    def as_dict(self, values: list) -> dict:
        return {f: self.init_value(f, val) for f, val in zip(self.fields, values)}


def join_schema(url: str, builder: SchemaBuilder) -> dict:
    for row in parse_csv(url):
        try:
            yield builder.as_dict(row)
        except:
            print('Error', row)
            pass


class Export(JsonIterator):
    event_builder = SchemaBuilder(relative_path(f'{config_base}/export.schema'))
    mention_builder = SchemaBuilder(relative_path(f'{config_base}/mention.schema'))

    def __init__(self):
        super().__init__()
        self.return_multiple = True

    def on_data(self, row: dict or None, *args):
        url = row
        if isinstance(row, list):
            url = url[0]
        if isinstance(url, dict):
            url = row.get("url")
        if 'export.CSV' in url:
            for row in join_schema(url, self.event_builder):
                yield row
        elif 'mentions.CSV' in url:
            for row in join_schema(url, self.mention_builder):
                yield row
