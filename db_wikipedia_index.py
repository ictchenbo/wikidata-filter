
if __name__ == '__main__':
    from wikidata_filter import run
    from wikidata_filter.loader import JsonLineFileLoader
    from wikidata_filter.iterator import Chain, RemoveFields, RenameFields, Count
    from wikidata_filter.iterator.database.elasticsearch import ESWriter

    remove_fields = ['site', 'categories', 'sections', 'pageID', 'isDisambiguation', 'isRedirect', 'isStub', 'redirectTo']

    def zhwiki():
        es_configs = {
            # 'host': '10.208.61.113',
            # 'port': 9200,
            # 'username': 'elastic',
            # 'password': 'golaxyintelligence',
            'index': 'zhwiki_v1'
        }

        processor = Chain(
            # CopyFields({"title": "id"}),
            RemoveFields(*remove_fields),
            RenameFields({'plaintext': 'text'}),
            ESWriter(**es_configs),
            Count(100)
        )

        input_file = r'C:\work\git2024\wikipedia-data\zhwiki-page.json'
        # "data/zhwiki-page3.json"
        run(JsonLineFileLoader(input_file), processor)

    def enwiki():
        es_configs = {
            # 'host': '10.208.61.113',
            # 'port': 9200,
            # 'username': 'elastic',
            # 'password': 'golaxyintelligence',
            'index': 'enwiki_v1'
        }

        processor = Chain(
            # CopyFields({"title": "id"}),
            RemoveFields(*remove_fields),
            RenameFields({'plaintext': 'text'}),
            ESWriter(**es_configs),
            Count(100)
        )

        input_file = r'C:\work\git2024\wikipedia-data\enwiki-page.json'
        run(JsonLineFileLoader(input_file), processor)

    enwiki()
