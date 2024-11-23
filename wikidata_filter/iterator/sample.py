"""对数据进行采样输出"""
from random import random
from .common import Filter
from wikidata_filter.util.jsons import extract as V


class Sample(Filter):
    """随机采样 保留特定比例的数据"""
    def __init__(self, rate: float = 0.1):
        super().__init__(self)
        self.rate = rate

    def __call__(self, *args, **kwargs):
        return random() <= self.rate


class Distinct(Filter):
    """去重，过滤掉重复数据 默认为本地set进行缓存判重，可实现基于内存数据库（如redis）或根据业务数据库进行重复监测"""
    def __init__(self, field: str):
        super().__init__(self)
        assert field is not None, "field 不能为空"
        self.field = field
        self.cache = set()

    def __call__(self, data: dict):
        val = V(data, self.field)
        return not self.exists(val)

    def exists(self, val):
        """判断特定的值是否存在 重写此方法实现更加持久性的判断"""
        if val in self.cache:
            return True
        self.cache.add(val)
        return False


class DistinctRedis(Distinct):
    """基于Redis进行缓存去重 具体待实现"""
    def __init__(self, field: str):
        super().__init__(field)
        raise NotImplemented()

    def exists(self, val):
        pass

