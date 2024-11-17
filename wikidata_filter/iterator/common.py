from wikidata_filter.iterator.base import JsonIterator


class Prompt(JsonIterator):
    """打印提示信息"""
    def __init__(self, msg: str):
        self.msg = msg

    def on_data(self, data, *args):
        print(self.msg)
        return data


class Print(JsonIterator):
    """
    打印数据，方便查看中间结果
    """
    def on_data(self, data, *args):
        print(data)
        return data


class Filter(JsonIterator):
    """
    过滤节点（1->?)
    根据提供的匹配函数判断是否继续往后面传递数据
    """
    def __init__(self, matcher):
        super().__init__()
        assert matcher is not None, "matcher should not be None"
        self.matcher = matcher

    def on_data(self, data, *args):
        if self.matcher(data):
            return data


class Count(JsonIterator):
    """
    计数节点 对流经的数据进行计数 并按照一定间隔进行打印输出
    """
    def __init__(self, ticks=1000, label: str = '-'):
        super().__init__()
        self.counter = 0
        self.ticks = ticks
        self.label = label

    def __process__(self, item, *args):
        if item is None:
            print(f'Counter[{self.label}] finish, total:', self.counter)
        else:
            self.counter += 1
            if self.counter % self.ticks == 0:
                print(f'Counter[{self.label}]:', self.counter)
        return item

    def __str__(self):
        return f"{self.name}(ticks={self.ticks},label='{self.label}')"
