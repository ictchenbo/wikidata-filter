if __name__ == '__main__':
    import sys

    from wikidata_filter import run
    from wikidata_filter.loader import JsonLineFileLoader
    from wikidata_filter.iterator import Chain, Count, Print, WriteJson
    from wikidata_filter.iterator.wikidata import ValuesFilter, AsRelation
    from wikidata_filter.util.file_loader import key_from_json

    input_file = sys.argv[1]
    input_file2 = sys.argv[2]
    output_file = sys.argv[3]

    human_set = key_from_json(input_file2)
    print('human total', len(human_set))

    chain = Chain(
        ValuesFilter(props_set=human_set),
        AsRelation(),
        Count(ticks=100),
        WriteJson(output_file)
    )

    run(JsonLineFileLoader(input_file), chain)
