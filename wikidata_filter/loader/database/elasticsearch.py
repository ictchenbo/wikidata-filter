from wikidata_filter.loader.base import DataProvider
import requests


class ES(DataProvider):
    """
    读取ES指定索引全部数据，支持提供查询条件
    """
    def __init__(self, host="localhost", port=9200, user=None, password=None, index=None, query: dict=None, batch_size=1000, **kwargs):
        self.url = f"http://{host}:{port}"
        self.cache = []
        self.batch_size = batch_size
        if password:
            self.auth = (user, password)
        else:
            self.auth = None
        self.index_name = index
        self.query = query
        self.scroll = "1m"
        self.batch_size = batch_size
        self.query_body = {
            'size': batch_size,
            'query': query if query else {'match_all': {}}
        }

    def iter(self):
        scroll_id = None
        while True:
            if scroll_id:
                # 后续请求
                url = f'{self.url}/_search/scroll'
                res = requests.post(url, auth=self.auth, json={'scroll': self.scroll, 'scroll_id': scroll_id})
            else:
                # 第一次请求 scroll
                url = f'{self.url}/{self.index_name}/_search?scroll={self.scroll}'
                res = requests.post(url, auth=self.auth, json=self.query_body)

            res = res.json()
            if '_scroll_id' in res:
                scroll_id = res['_scroll_id']

            if 'hits' not in res or 'hits' not in res['hits']:
                print('ERROR', res)
                continue

            hits = res['hits']['hits']
            for hit in hits:
                doc = hit['_source']
                yield doc

            if len(hits) < self.batch_size:
                # clear scroll
                url = f'{self.url}/_search/scroll'
                requests.delete(url, auth=self.auth, json={'scroll_id': scroll_id})
                break
