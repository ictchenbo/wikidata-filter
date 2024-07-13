
from wikidata_filter.loader.base import DataProvider

try:
    from clickhouse_driver import Client
except:
    print('install clickhouse_driver first!')
    raise "clickhouse_driver not installed"


class CKLoader(DataProvider):
    def __init__(self, host='localhost', port=9000, user="default", password="", database='default', table=None, select="*", where=None, limit=None, **kwargs):
        self.select = select
        self.table = table
        self.where = where
        self.limit = limit
        self.client = Client(host=host,
                             port=port,
                             database=database,
                             user=user,
                             password=password,
                             send_receive_timeout=20)

    def iter(self):
        for row in self.fetch_all(format="json"):
            yield row

    def fetch_all(self, format="tuple"):
        query = f'select {self.select} from {self.table}'
        if self.where:
            query = query + " where " + self.where
        if self.limit:
            query = query + f" limit {self.limit}"
        print("Query:", query)

        if format.lower() == "json":
            cols = None
            for row in self.client.execute_iter(query, with_column_types=True):
                if cols is None:
                    cols = row
                    continue
                yield {cols[i][0]: row[i] for i in range(len(row))}

        return self.client.execute_iter(query)
