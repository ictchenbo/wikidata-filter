if __name__ == '__main__':
    import sys

    from wikidata_filter import run
    from wikidata_filter.loader import JsonLineFileLoader
    from wikidata_filter.iterator import Chain, Filter, WriteJson
    from wikidata_filter.iterator.wikidata import PropsFilter
    from wikidata_filter.matcher.wikidata import WikidataMatcherV2

    from wikidata_filter.util.file_loader import get_lines_part

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    chain = Chain(
        Filter(WikidataMatcherV2({"P31": get_lines_part('config/event_type.txt')})),
        WriteJson(output_file)
    )

    run(JsonLineFileLoader(input_file), chain)
