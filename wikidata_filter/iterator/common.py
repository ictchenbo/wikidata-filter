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
    def __init__(self, matcher, key: str = None):
        super().__init__()
        assert matcher is not None, "matcher should not be None"
        self.matcher = matcher
        self.key = key

    def on_data(self, data, *args):
        if self.key and self.key not in data:
            print(f"Warning: `{self.key}` not exists")
        val = data
        if self.key:
            val = data[self.key]
        if self.matcher(val):
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

    def on_data(self, item, *args):
        self.counter += 1
        if self.counter % self.ticks == 0:
            print(f'Counter[{self.label}]:', self.counter)
        return item

    def on_complete(self):
        print(f'Counter[{self.label}] finish, total:', self.counter)

    def __str__(self):
        return f"{self.name}(ticks={self.ticks},label='{self.label}')"


class BlackList(Filter):
    """黑名单过滤 匹配黑名单的被过滤掉"""
    def __init__(self, cache: dict or set, key: str):
        super().__init__(self, key)
        self.cache = cache

    def __call__(self, val, *args, **kwargs):
        return val not in self.cache


class WhiteList(Filter):
    """白名单过滤 匹配白名单的才保留"""
    def __init__(self, cache: dict or set, key: str):
        super().__init__(self, key)
        self.cache = cache

    def __call__(self, val, *args, **kwargs):
        return val in self.cache
