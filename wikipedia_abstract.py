
if __name__ == '__main__':
    import sys
    from wikidata_filter.iterator import Chain, Count, WriteJson
    from wikidata_filter.transform.wikipedia import *
    # input_file = r'zhwiki-latest-abstract.xml.gz'
    input_file = sys.argv[1]
    # wikipedia-page.json
    output_file = sys.argv[2]

    processor = Chain(Count(ticks=1000), WriteJson(output_file))
    abstract_xml_dump(input_file, processor)
