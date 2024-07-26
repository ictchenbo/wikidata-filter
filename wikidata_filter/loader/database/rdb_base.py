from wikidata_filter.loader.base import DataProvider


class RDBBase(DataProvider):
    conn = None

    def __init__(self, database='default', table=None, select="*", where=None, limit=None, **kwargs):
        self.database = database
        self.table = table
        self.select = select
        self.where = where
        self.limit = limit

    def iter(self):
        query = f'select {self.select} from {self.table}'
        if self.where:
            query = query + " where " + self.where
        if self.limit:
            query = query + f" limit {self.limit}"
        print("Query:", query)

        for row in self.fetch_all(query, fmt="json"):
            yield row

    def fetch_all(self, query: str, fmt="tuple"):
        cursor = self.conn.cursor()
        cursor.execute(query)

        # count_sql = 'select count(*) as totalCount from {0};'.format(table)
        # cursor.execute(count_sql)
        # data_count = cursor.fetchall()[0][0]

        if fmt.lower() == "json":
            col_name_list = [tup[0] for tup in cursor.description]
            for item in cursor.fetchall():
                rec = dict(zip(col_name_list, list(item)))
                yield rec

        return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
