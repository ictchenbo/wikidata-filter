
if __name__ == '__main__':
    import sys
    from wikidata_filter.iterator import Chain, WriteJson, Count
    from wikidata_filter.iterator.wikipedia import ToHTML, Abstract
    from wikidata_filter.transform.wikipedia import *

    # input4 = r'data/zhwiki-latest-pages-articles.xml.bz2'
    input_file = sys.argv[1]
    # 'zhwiki-page.json'
    output_file = sys.argv[2]
    # 'data/zhwiki-html'

    processor = Chain(Count(ticks=1000), Abstract(), WriteJson(output_file))
    # WikipediaHTML('data/zhwiki-html')
    page_xml_dump(input_file, processor)
