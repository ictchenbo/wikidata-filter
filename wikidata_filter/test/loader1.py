from typing import Iterable, Any

from wikidata_filter.loader.base import DataProvider


class MyLoader(DataProvider):
    def iter(self) -> Iterable[Any]:
        for i in range(10):
            yield i
