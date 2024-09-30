
import requests
from wikidata_filter.iterator.base import JsonIterator


READER_API_BASE = "https://r.jina.ai/"
READER_API_KEY = "jina_546c74213c784959a87c39b75a6efdaeQxwqYuQ-tIfMcHyO70FMWQNraqAb"
READER_API_HEADER = {"Authorization": f"Bearer {READER_API_KEY}"}


class ReaderAPI(JsonIterator):
    def on_data(self, row: dict or None, *args):
        url = row
        if isinstance(url, list):
            url = url[0]
        if isinstance(url, dict):
            url = url["url"]
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        res = requests.get(READER_API_BASE + url, headers=READER_API_HEADER)
        text = res.text
        return {
            "url": url,
            "content": text
        }
