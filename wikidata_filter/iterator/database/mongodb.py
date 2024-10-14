
from wikidata_filter.iterator.common import BufferedWriter


class MongoWriter(BufferedWriter):
    def __init__(self, host='localhost', port=27017, username=None, password=None, auth_db='admin', database='default', collection=None, buffer_size: int = 1000, **kwargs):
        super().__init__(buffer_size)
        try:
            import pymongo
        except:
            print('install pymongo first!')
            raise "pymongo not installed"

        self.client = pymongo.MongoClient(host=host, port=port)
        if username:
            self.client[auth_db].authenticate(username, password)
        self.db = self.client[database]
        self.coll = self.db[collection]

    def write_batch(self, rows: list):
        try:
            self.coll.insert_many(rows)
            return True
        except Exception as e:
            print(e)
            return False
