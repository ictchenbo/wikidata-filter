from wikidata_filter.loader.database.rdb_base import RDBBase


class PostgresSQLLoader(RDBBase):
    def __init__(self, host='localhost', port=9000, user="default", password="", database='default', table=None, select="*", where=None, limit=None, **kwargs):
        super().__init__(database=database, table=table, select=select, where=where, limit=limit)
        try:
            import psycopg2
        except ImportError:
            print('install import psycopg2 first!')
            raise "import psycopg2 not installed"

        self.conn = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
