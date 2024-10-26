from wikidata_filter.iterator.base import JsonIterator


class Prompt(JsonIterator):
    def __init__(self, msg: str):
        self.msg = msg

    def on_data(self, data: dict or None, *args):
        print(self.msg)
        return data


class Print(JsonIterator):
    """
    打印节点
    """
    def on_data(self, data: dict or None, *args):
        print(data)
        return data


class Filter(JsonIterator):
    """
    过滤节点 根据提供的匹配函数判断是否继续往后面传递数据
    """
    def __init__(self, matcher):
        super().__init__()
        self.matcher = matcher

    def on_data(self, data: dict or None, *args):
        if self.matcher(data):
            return data


class Count(JsonIterator):
    """
    计数节点 对流经的数据进行计数 并按照一定间隔进行打印输出
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


class BufferBase(JsonIterator):
    """
    缓冲基类 到达的数据先根据一定规则进行缓存，等待后续达到限额或数据整体处理结果再向后传递。
    数据结束时需要发送一个None作为结束信号
    """


class Buffer(BufferBase):
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


class BufferedWriter(JsonIterator):
    def __init__(self, buffer_size=1000):
        self.buffer = []
        self.buffer_size = buffer_size

    def on_data(self, data: dict or None, *args):
        if not isinstance(data, list):
            self.buffer.append(data)
        else:
            self.buffer.extend(data)
        if len(self.buffer) >= self.buffer_size:
            self.write_batch(self.buffer)
            self.buffer.clear()

        return data

    def write_batch(self, data: list):
        pass

    def on_complete(self):
        if self.buffer:
            self.write_batch(self.buffer)
            self.buffer.clear()


class Reduce(BufferBase):
    """对数据进行规约 向后传递规约结果"""
    pass
