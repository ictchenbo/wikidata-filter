
if __name__ == '__main__':
    from wikidata_filter.util.file_loader import get_lines_part

    from wikidata_filter import run
    from wikidata_filter.loader.database.elasticsearch import ESLoader

    from wikidata_filter.iterator import Filter, Chain, Count, Buffer
    from wikidata_filter.iterator.database.clickhouse import CKWriter

    id_set = get_lines_part('data/entity_id.csv')

    print('load total ID', len(id_set))

    es_configs = {
        'host': '10.208.61.113',
        'port': 9200,
        'username': 'elastic',
        'password': 'golaxyintelligence',
        'index': 'entity_share_data_30'
    }

    ck_configs = {
        'host': '10.208.57.5',
        'port': 59000,
        'database': 'goin_kjqb_230202_v_3_0',
        'table': 'entity_share_data_shard',  # write to shard table ONLY
        'buffer_size': 1000
    }

    chain = Chain(
        # Count(ticks=10000, label='ES-Scroll'),
        Filter(matcher=lambda item: item.get('mongo_id') not in id_set),
        Count(ticks=1000, label='Row-Filter'),
        CKWriter(**ck_configs)
    )

    run(ESLoader(**es_configs), chain)
