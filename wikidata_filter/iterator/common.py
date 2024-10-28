from wikidata_filter.iterator.base import JsonIterator


class Prompt(JsonIterator):
    """打印提示信息"""
    def __init__(self, msg: str):
        self.msg = msg

    def on_data(self, data: dict or None, *args):
        print(self.msg)
        return data


class Print(JsonIterator):
    """
    打印数据，方便查看中间结果
    """
    def on_data(self, data: dict or None, *args):
        print(data)
        return data


class Filter(JsonIterator):
    """
    过滤节点（1->?)
    根据提供的匹配函数判断是否继续往后面传递数据
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
        self.ticks = ticks
        self.label = label

    def on_data(self, item: dict or None, *args):
        self.counter += 1
        if self.counter % self.ticks == 0:
            print(f'Counter[{self.label}]', self.counter)
        return item

    def on_complete(self):
        print(f'Counter[{self.label}] total', self.counter)


class Reduce(JsonIterator):
    """对数据进行规约(many->1/0) 向后传递规约结果"""
    pass


class Buffer(Reduce):
    """
    缓冲节点 当到达的数据填满缓冲池后再一起向后传递。主要用于批处理场景。
    未来可以扩展 如带时限的缓冲
    """
    def __init__(self, buffer_size=100, mode="batch"):
        """
        :param buffer_size 缓冲池大小
        :param mode 数据传递模式，batch表示批量传递 否则为普通模式 默认为batch模式
        """
        self.buffer_size = buffer_size
        self.buffer = []
        self.mode = mode

    def on_data(self, item: dict or None, *args):
        self.buffer.append(item)
        # if full
        if len(self.buffer) >= self.buffer_size:
            temp = self.buffer
            self.commit(temp)
            self.buffer = []  # 当前缓冲池清空
            if self.mode == "buffer":
                return temp  # 往后传递数据
        if self.mode == "buffer":
            return None  # 不需要往后传递任何数据
        else:
            return item

    def commit(self, buffer: list):
        """提交当前缓冲数据 比如写入数据库或文件"""
        print("buffer data commited, num of rows:", len(buffer))

    def on_complete(self):
        if self.buffer:
            self.commit(self.buffer)
            self.buffer.clear()


class BufferedWriter(Buffer):
    """缓冲写 比如数据库或文件算子 默认作为普通算子加入流程"""
    def __init__(self, buffer_size=1000, mode="single"):
        super().__init__(buffer_size, mode=mode)

    def commit(self, buffer: list):
        self.write_batch(buffer)

    def write_batch(self, data: list):
        pass
