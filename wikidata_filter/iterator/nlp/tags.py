import re
from wikidata_filter.iterator.base import JsonIterator


def split(text: str):
    if not text:
        return []
    if ':' in text:
        text = text[text.find(':') + 1:]
    if '：' in text:
        text = text[text.find('：') + 1:]
    parts = re.split('[;；。]+', text)
    return [p.strip() for p in parts]


class Splitter(JsonIterator):
    def __init__(self, *keys):
        self.keys = keys

    def on_data(self, data: dict, *args):
        for key in self.keys:
            if key in data:
                data[key] = split(data.get(key))
        return data
