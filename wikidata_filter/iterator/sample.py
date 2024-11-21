"""对数据进行采样输出"""
from random import random
from .common import Filter


class Sample(Filter):
    def __init__(self, rate: float = 0.1):
        super().__init__(self)
        self.rate = rate

    def __call__(self, *args, **kwargs):
        v = random()
        return v <= self.rate

