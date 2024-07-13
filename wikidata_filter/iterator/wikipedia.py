import os

from wikidata_filter.iterator.base import JsonIterator

from wikimarkup.parser import Parser


class ToHTML(JsonIterator):
    """
    输入wikipedia 生成对应的HTML文件
    """
    parser = Parser()

    def __init__(self, output_dir: str, title_key='title', content_key='content'):
        super().__init__()
        self.output_dir = output_dir
        self.title_key = title_key
        self.content_key = content_key
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    def on_data(self, item: dict, *args):
        content = item.get(self.content_key)
        filename = item.get(self.title_key)
        if filename and content:
            with open(os.path.join(self.output_dir, f'{filename}.html'), 'w', encoding='utf8') as fout:
                fout.write(self.parser.parse(content))
        return item


class PageAbstract(JsonIterator):
    """
    基于wikipedia文本，提取第一段作为摘要
    """
    def on_data(self, item: dict, *args):
        text = item.get('text')
        if text:
            pos = text.find('\n\n')
            if pos > 0:
                item['abstract'] = text[0:pos]
        return item
