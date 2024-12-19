from typing import Iterable, Any

from wikidata_filter.loader.base import DataProvider
from wikidata_filter.loader.database.rdb_base import RDBBase


class DBTables(DataProvider):
    """获取数据库的表"""
    def __init__(self, loader: RDBBase, *database_list):
        self.loader = loader
        self.database_list = database_list

    def iter(self) -> Iterable[Any]:
        if self.database_list:
            for db in self.database_list:
                for table in self.loader.list_tables(db):
                    yield {
                        "name": table,
                        "columns": self.loader.desc_table(table, db),
                        "database": db
                    }
        else:
            for table in self.loader.list_tables():
                yield {
                    "name": table,
                    "columns": self.loader.desc_table(table)
                }

    def close(self):
        self.loader.close()
