from random import random


class DataProvider:
    """数据提供器接口 为流程供给数据"""
    def iter(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.iter()

    def close(self):
        pass


class ArrayProvider(DataProvider):
    """基于数组提供数据"""
    def __init__(self, data: list):
        self.data = data

    def iter(self):
        for item in self.data:
            yield item


class TextProvider(DataProvider):
    """基于文本提供数据 按照指定分隔符进行分割"""
    def __init__(self, text: str, sep: str = '\n'):
        self.data = text
        self.sep = sep

    def iter(self):
        for item in self.data.split(self.sep):
            yield item


class RandomGenerator(DataProvider):
    def __init__(self, num_of_times: int = 0):
        self.num_of_times = num_of_times

    def iter(self):
        if self.num_of_times > 0:
            for i in range(self.num_of_times):
                yield random()
        else:
            while True:
                yield random()
