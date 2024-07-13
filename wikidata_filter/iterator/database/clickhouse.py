import json
from wikidata_filter.iterator.database.base import BufferedWriter
from clickhouse_driver import Client


class CKWriter(BufferedWriter):
    """
    数据写入CK中
    """
    def __init__(self, host='localhost', port=9000, user="default", password="", database='default', table=None, buffer_size=1000, **kwargs):
        super().__init__(buffer_size=buffer_size)
        self.table = table
        self.client = Client(host=host,
                             port=port,
                             database=database,
                             user=user,
                             password=password,
                             send_receive_timeout=20)

    def write_batch(self, rows: list):
        json_data = [json.dumps(row, ensure_ascii=False) for row in rows]
        sql = f"insert into {self.table} format JSONEachRow {','.join(json_data)}"
        try:
            self.client.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False
