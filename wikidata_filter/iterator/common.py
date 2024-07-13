from wikidata_filter.iterator.base import JsonIterator


class Filter(JsonIterator):
    """
    匹配筛选
    """
    def __init__(self, matcher):
        super().__init__()
        self.matcher = matcher

    def on_data(self, data: dict or None, *args):
        if self.matcher(data):
            return data


class Print(JsonIterator):
    """
    打印节点
    """
    def on_data(self, data: dict or None, *args):
        print(data)
        return data


class Count(JsonIterator):
    """
    计数节点
    """
    def __init__(self, ticks=1000, label: str = '-'):
        super().__init__()
        self.counter = 0
        self.interval = ticks
        self.label = label

    def on_data(self, item: dict or None, *args):
        self.counter += 1
        if self.counter % self.interval == 0:
            print(f'Counter[{self.label}]', self.counter)
        return item

    def on_complete(self):
        print(f'Counter[{self.label}] total', self.counter)


class Buffer(JsonIterator):
    """
    缓冲节点 当到达的数据填满缓冲池后再一起向后传递。主要用于批处理场景.
    注意：当数据结束时，需要发送一个None作为结束信号
    """

    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        self.buffer = []

    def on_data(self, item: dict or None, *args):
        # end of data
        if item is None:
            return self.buffer or None
        # when full
        if len(self.buffer) == self.batch_size:
            self.buffer.clear()
        # append
        self.buffer.append(item)
        # if full
        if len(self.buffer) == self.batch_size:
            return self.buffer
        return None
