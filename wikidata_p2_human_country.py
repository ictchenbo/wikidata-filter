if __name__ == '__main__':
    import sys

    from wikidata_filter import run
    from wikidata_filter.loader import JsonLineFileLoader
    from wikidata_filter.iterator import Chain, Filter, WriteJson
    from wikidata_filter.matcher.wikidata import WikidataMatcherV2

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    country_list = sys.argv[3].split(',')

    # USA "Q30"
    # China "Q148", "Q865"
    matcher = WikidataMatcherV2({"P27": country_list})

    chains = Chain(Filter(matcher), WriteJson(output_file))

    run(JsonLineFileLoader(input_file), chains)
