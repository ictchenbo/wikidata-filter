import time
from typing import Iterable, Any
from random import random
from wikidata_filter.util.dates import current_time


class DataProvider:
    """数据提供器接口 为流程供给数据"""
    def iter(self) -> Iterable[Any]:
        pass

    def __call__(self, *args, **kwargs):
        return self.iter()

    def close(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return f'{self.name}'


class Array(DataProvider):
    """基于数组提供数据"""
    def __init__(self, data: list):
        self.data = data

    def iter(self):
        for item in self.data:
            yield item


class String(DataProvider):
    """基于文本提供数据 按照指定分隔符进行分割"""
    def __init__(self, text: str, sep: str = '\n'):
        self.data = text
        self.sep = sep

    def iter(self):
        for item in self.data.split(self.sep):
            yield item


class Random(DataProvider):
    """随机生成器"""
    def __init__(self, num_of_times: int = 0):
        self.num_of_times = num_of_times

    def iter(self):
        if self.num_of_times > 0:
            for i in range(self.num_of_times):
                yield random()
        else:
            while True:
                yield random()


class TimedLoader(DataProvider):
    """定时轮询器 定时无限（或指定次数）调用提供的Loader 比如定时进行数据库轮询或接口轮询"""
    def __init__(self, that: DataProvider, interval: int = 15, num_of_times: int = 0):
        self.that = that
        self.interval = interval
        self.num_of_times = num_of_times

    def iter(self):
        counter = 0
        while True:
            print(f"{self} running at: ", current_time())
            counter += 1
            for item in self.that.iter():
                yield item

            if 0 < self.num_of_times <= counter:
                break

            time.sleep(self.interval)

    def __str__(self):
        return f"TimedPull[{self.that.name}, interval={self.interval}]"


class Function(DataProvider):
    """函数调用包装器 提供调用函数的结果"""
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def iter(self):
        res = self.function(*self.args, **self.kwargs)
        yield res
