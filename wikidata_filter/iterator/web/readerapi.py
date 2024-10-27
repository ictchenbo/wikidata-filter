
import requests
from wikidata_filter.iterator.base import JsonIterator


READER_API_BASE = "https://r.jina.ai/"


class ReaderAPI(JsonIterator):
    headers: dict = {}

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if api_key:
            self.headers = {"Authorization": f"Bearer {api_key}"}

    def on_data(self, row: dict or None, *args):
        url = row
        if isinstance(url, list):
            url = url[0]
        if isinstance(url, dict):
            url = url["url"]
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        res = requests.get(READER_API_BASE + url, headers=self.headers)
        text = res.text
        return {
            "url": url,
            "content": text
        }
