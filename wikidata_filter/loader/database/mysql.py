from wikidata_filter.loader.database.rdb_base import RDBBase

try:
    import pymysql
except ImportError:
    print('install pymysql first!')
    raise "pymysql not installed"


class MySQL(RDBBase):
    def __init__(self, host='localhost', port=3306, user="root", password="", database=None, paging=False, **kwargs):
        super().__init__(database=database, paging=paging, **kwargs)

        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.SSCursor
        )
