from wikidata_filter.loader.base import DataProvider
from wikidata_filter.util.web_util import get_text


url_all_file = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
url_latest_file = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"


def get_page_parse(url):
    content = get_text(url)
    if content:
        for row in content.split('\n'):
            parts = row.split()
            if len(parts) < 3:
                continue
            yield {
                "url": parts[2],
                "file_size": int(parts[0])
            }


class GdeltAll(DataProvider):
    """
    获取GDELT全部更新列表 解析相关文件URL
    """
    def iter(self):
        return get_page_parse(url_all_file)


class GdeltLatest(DataProvider):
    """
    获取GDELT最近更新文件列表 解析相关文件URL
    """
    def __init__(self, times_of_requests: int = 1):
        self.times_of_requests = times_of_requests

    def iter(self):
        forever = self.times_of_requests == 0
        run_times = 0
        while forever or run_times < self.times_of_requests:
            for row in get_page_parse(url_latest_file):
                yield row
            run_times += 1
            print(f"request for {run_times} times")
