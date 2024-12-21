import sys
from wikidata_filter.wikipedia import *
from wikidata_filter.iterator import Chain, WriteJson, Count


def process_page():
    from wikidata_filter.iterator.wikipedia import Abstract

    processor = Chain(Count(ticks=1000), Abstract(), WriteJson(output_file))
    # WikipediaHTML('data/zhwiki-html')
    page_xml_dump(input_file, processor)


def process_abstract():
    processor = Chain(Count(ticks=1000), WriteJson(output_file))
    abstract_xml_dump(input_file, processor)


if __name__ == '__main__':
    # input_file = r'zhwiki-latest-abstract.xml.gz'
    input_file = sys.argv[1]
    # wikipedia-page.json
    output_file = sys.argv[2]

    # input4 = r'data/zhwiki-latest-pages-articles.xml.bz2'
    # input_file = sys.argv[1]
    # 'zhwiki-page.json'
    # output_file = sys.argv[2]
    # 'data/zhwiki-html'
