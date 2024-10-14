from wikidata_filter.loader.base import DataProvider


class MongoLoader(DataProvider):
    def __init__(self, host='localhost', port=27017, username=None, password=None, auth_db='admin', database='default', collection=None, query: dict = None, limit=None, **kwargs):
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
        self.query = query
        self.limit = limit

    def iter(self):
        cursor = self.coll.find(self.query)
        if self.limit is not None and self.limit > 0:
            cursor.limit(self.limit)
        for doc in cursor:
            yield doc

    def close(self):
        self.client.close()
