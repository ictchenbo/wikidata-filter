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

    def on_data(self, data: dict or None, *args):
        if self.key:
            if self.key in data:
                data[self.target_key] = self.mapper(data[self.key])
            else:
                print("Warning, no such field:", self.key)
            return data
        else:
            return self.mapper(data)

    def __str__(self):
        return f'{self.name}[key={self.key}, target_key={self.target_key}]'


class Flat(JsonIterator):
    """
    扁平化操作（1-*）
    如果未提供key，对整个输入进行扁平化：
      - 对于数组 arr -> iterator(arr)
      - 对于字典：如果flat_mode='key'，则对key打散，否则对value打散
    如果提供了key，则针对该字段进行上述扁平化。
    """
    return_multiple = True

    def __init__(self, key: str = None, flat_mode: str = 'value', inherit_props: bool = False):
        self.key = key
        self.flat_mode = flat_mode
        self.inherit_props = inherit_props

    def new_item(self, data: dict, item):
        ret = dict(**data)
        ret[self.key] = item
        return ret

    def on_data(self, data, *args):
        if data is None:
            return []
        _data = data.get(self.key) if self.key else data
        _data = self.transform(_data)
        if isinstance(_data, list) or isinstance(_data, tuple):
            if self.inherit_props and isinstance(data, dict):
                for item in _data:
                    yield self.new_item(data, item)
            else:
                for item in _data:
                    yield item
        elif isinstance(_data, dict):
            if self.flat_mode == 'key':
                for key in _data.keys():
                    yield key
            else:
                for key, val in _data.items():
                    if isinstance(val, dict):
                        val["_key"] = key
                    yield val
        else:
            yield data

    def transform(self, data):
        return data

    def __str__(self):
        return f"{self.name}(key='{self.key}', flat_mode='{self.flat_mode}')"


class FlatMap(Flat):
    """
    根据mapper结果进行扁平化 如果提供了key，则是对该字段调用mapper 否则是对输入数据调用mapper
    """
    def __init__(self, mapper, key: str = None, flat_mode: str = 'value'):
        super().__init__(key=key, flat_mode=flat_mode)
        self.mapper = mapper

    def transform(self, data):
        return self.mapper(data)
