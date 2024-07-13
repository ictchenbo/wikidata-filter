if __name__ == '__main__':
    import sys

    from wikidata_filter import run
    from wikidata_filter.loader import JsonLineFileLoader
    from wikidata_filter.iterator import Chain, Filter, WriteJson
    from wikidata_filter.iterator.wikidata import IDNameMap

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    chain = Chain(
        IDNameMap(),
        WriteJson(output_file)
    )

    run(JsonLineFileLoader(input_file), chain)
