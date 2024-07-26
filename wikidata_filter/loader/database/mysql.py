from wikidata_filter.loader.database.rdb_base import RDBBase


class MySQLLoader(RDBBase):
    def __init__(self, host='localhost', port=9000, user="default", password="", database='default', table=None, select="*", where=None, limit=None, **kwargs):
        super().__init__(database=database, table=table, select=select, where=where, limit=limit)
        try:
            import pymysql
        except ImportError:
            print('install pymysql first!')
            raise "pymysql not installed"

        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database,
            charset='utf8'
        )
