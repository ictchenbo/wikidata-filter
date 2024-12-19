from wikidata_filter.loader.database.rdb_base import RDBBase

try:
    import psycopg2
except ImportError:
    print('install import psycopg2 first!')
    raise "import psycopg2 not installed"


class PG(RDBBase):
    def __init__(self, host='localhost', port=9000, user="default", password="", database='default', **kwargs):
        super().__init__(database=database, **kwargs)
        self.conn = psycopg2.connect(host=host, port=port, user=user, password=password, database=database)
