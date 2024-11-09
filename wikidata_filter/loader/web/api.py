from wikidata_filter.loader.base import DataProvider

from wikidata_filter.util.web_util import get_json


class URLSimple(DataProvider):
    """直接请求URL，结果作为JSON"""
    def __init__(self, url: str, **kwargs):
        self.url = url

    def iter(self):
        c = get_json(self.url)
        yield c

    def __str__(self):
        return f'URLSimple[url={self.url}]'