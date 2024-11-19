from typing import Any

from wikidata_filter.iterator.base import JsonIterator


class Map(JsonIterator):
    """
    Map操作(1-1) 如果提供了key则针对字段进行Map操作
    """
    def __init__(self, mapper, key: str = None, target_key: str = None):
        super().__init__()
        self.key = key
        self.mapper = mapper
        self.target_key = target_key or key

    def on_data(self, data: Any, *args):
        if self.key:
            if isinstance(data, dict):
                if self.key in data:
                    data[self.target_key] = self.mapper(data[self.key])
                else:
                    print("Warning, no such field:", self.key)
            else:
                print("Warning, data is not dict:", data)
            return data
        else:
            return self.mapper(data)

    def __str__(self):
        return f"{self.name}(key='{self.key}', target_key='{self.target_key}')"


class Flat(JsonIterator):
    """
    扁平化操作（1-*）
    如果未提供key，对整个输入进行扁平化：
      - 对于数组 arr -> iterator(arr)
      - 对于字典：如果flat_mode='key'，则对key打散，否则对value打散
    如果提供了key，则针对该字段进行上述扁平化。
    """
    def __init__(self, key: str = None, flat_mode: str = 'kv', inherit_props: bool = False):
        self.key = key
        self.flat_mode = flat_mode
        self.inherit_props = inherit_props
        if inherit_props:
            assert self.key is not None, "key should not be None if inherit_props=True"

    def new_item(self, data: dict, item):
        if isinstance(item, dict):
            # 子项为字典 避免被继承字段覆盖。如果需要用继承字段 可以先重命名
            for k, v in data.items():
                if k != self.key:
                    item[k] = v
            return item
        else:
            # 子项为非字典
            ret = dict(**data)
            ret[self.key] = item
            return ret

    def on_data(self, data: Any, *args):
        if self.key and not isinstance(data, dict):
            print('Flat Warning: data must be dict if the key is specified')
            return data
        _data = data.get(self.key) if self.key else data
        _data = self.transform(_data)
        if isinstance(_data, list) or isinstance(_data, tuple):
            if self.inherit_props and isinstance(data, dict):
                # 字段继承
                for item in _data:
                    yield self.new_item(data, item)
            else:
                # 不继承 直接返回
                for item in _data:
                    yield item
        elif isinstance(_data, dict):
            # 对字典数据 提供三种扁平化方式，适合整齐KV字典转换为列表
            if self.flat_mode == 'kv':
                # 返回K-V对
                for key, val in _data.items():
                    yield key, val
            elif self.flat_mode == 'key':
                # 返回Key，适合整齐KV字典
                for key in _data.keys():
                    yield key
            elif self.flat_mode == 'value':
                # 返回Key，适合整齐KV字典
                for key, val in _data.items():
                    if isinstance(val, dict):
                        val["_key"] = key
                    yield val
        else:
            return data

    def transform(self, data):
        return data

    def __str__(self):
        key = f"'{self.key}'" if self.key else None
        return f"{self.name}(key={key}, flat_mode='{self.flat_mode}', inherit_props={self.inherit_props})"


class FlatMap(Flat):
    """
    根据mapper结果进行扁平化 如果提供了key，则是对该字段调用mapper 否则是对输入数据调用mapper
    """
    def __init__(self, mapper, key: str = None, flat_mode: str = 'value'):
        super().__init__(key=key, flat_mode=flat_mode)
        self.mapper = mapper

    def transform(self, data):
        return self.mapper(data)


class FlatProperty(Flat):
    """获取指定key的字段值进行返回，支持合并其他字段。相当于对object字段做提升"""
    def __init__(self, *keys, inherit_props: bool = False):
        super().__init__()
        assert len(keys) > 0, "必须指定一个或多个字段名称"
        if isinstance(keys[0], list) or isinstance(keys[0], tuple):
            self.keys = keys[0]
        else:
            self.keys = keys
        self.inherit_props = inherit_props

    def on_data(self, data: dict, *args):
        for key in self.keys:
            if key not in data:
                continue
            val = data[key]
            if self.inherit_props:
                for k, v in data.items():
                    if k not in self.keys:
                        val[k] = v
            yield val

    def __str__(self):
        return f"{self.name}(keys={self.keys}, inherit_props={self.inherit_props})"
