from wikidata_filter.loader.database.rdb_base import RDBBase


class CKLoader(RDBBase):
    def __init__(self, host='localhost', tcp_port=9000, username="default", password="", database='default', table=None, select="*", where=None, limit=None, **kwargs):
        super().__init__(database=database, table=table, select=select, where=where, limit=limit)
        try:
            from clickhouse_driver import Client
        except:
            print('install clickhouse_driver first!')
            raise "clickhouse_driver not installed"
        self.client = Client(host=host,
                             port=tcp_port,
                             database=database,
                             user=username,
                             password=password,
                             send_receive_timeout=20)
        print('connected to CK', host, tcp_port, database)

    def fetch_all(self, query: str, fmt="tuple"):
        if fmt.lower() == "json":
            cols = None
            for row in self.client.execute_iter(query, with_column_types=True):
                if cols is None:
                    cols = row
                    continue
                yield {cols[i][0]: row[i] for i in range(len(row))}

        return self.client.execute_iter(query)
