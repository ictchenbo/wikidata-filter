import json
from wikidata_filter.iterator.base import JsonIterator
from wikidata_filter.iterator.edit import Map
from wikidata_filter.util.jsons import extract, fill


class Select(JsonIterator):
    """
    Select操作 key支持嵌套，如`user.name`表示user字段下面的name字段 并将name作为结果字段名
    """
    def __init__(self, *keys, short_key: bool = False):
        assert len(keys) > 0, "必须指定一个或多个字段名称"
        if isinstance(keys[0], list) or isinstance(keys[0], tuple):
            self.keys = keys[0]
        else:
            self.keys = keys
        self.short_key = short_key
        self.path = {}
        for key in self.keys:
            path = key.split('.')
            if short_key:
                key = path[-1]
            self.path[key] = path

    def on_data(self, data: dict, *args):
        return {key: extract(data, path) for key, path in self.path.items()}

    def __str__(self):
        return f"{self.name}(keys={self.keys}, short_key={self.short_key})"


class SelectVal(JsonIterator):
    """
    字段值选择操作 指定字段key的值作为新的数据返回
    """
    def __init__(self, key: str, inherit_props: bool = False):
        self.key = key
        self.inherit_props = inherit_props

    def on_data(self, data: dict, *args):
        if not isinstance(data, dict):
            print("SelectVal Warning: data must be dict")
            return data
        keyval = data.get(self.key)
        if self.inherit_props:
            if isinstance(keyval, dict):
                for k, v in data.items():
                    if k != self.key:
                        keyval[k] = v
            else:
                print("SelectVal Warning: field value must be dict when inherit_props is True")
            return keyval

    def __str__(self):
        return f"{self.name}('{self.key}', inherit_props={self.inherit_props})"


class RemoveFields(JsonIterator):
    """
    移除部分字段
    """
    def __init__(self, *keys):
        super().__init__()
        if keys:
            if isinstance(keys[0], list) or isinstance(keys[0], tuple):
                self.keys = keys[0]
            else:
                self.keys = keys

    def on_data(self, data: dict, *args):
        return {k: v for k, v in data.items() if k not in self.keys}

    def __str__(self):
        return f"{self.name}(keys={self.keys})"


class DictEditBase(JsonIterator):
    templates: dict = {}

    def __init__(self, tmp: dict):
        self.templates = tmp

    def __str__(self):
        return f"{self.name}(**{self.templates})"


class AddFields(DictEditBase):
    """添加字段 如果不存在"""
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def on_data(self, data: dict, *args):
        for k, v in self.templates.items():
            if k not in data:
                data[k] = v
        return data


class RenameFields(DictEditBase):
    """对字段重命名"""
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def on_data(self, data: dict, *args):
        for s, t in self.templates.items():
            if s in data:
                data[t] = data.pop(s)
        return data


class UpdateFields(DictEditBase):
    """更新字段，Upsert模式"""
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def on_data(self, data: dict, *args):
        for s, t in self.templates.items():
            data[t] = data[s]
        return data


class CopyFields(DictEditBase):
    """复制已有的字段 如果目标字段名存在 则覆盖"""
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def on_data(self, data: dict, *args):
        for s, t in self.templates.items():
            data[t] = data.get(s)
        return data


class InjectField(JsonIterator):
    """
    基于给定的KV缓存对当前数据进行填充
    """
    def __init__(self, kv: dict, inject_path: str or list, reference_path: str):
        self.kv = kv
        self.inject_path = inject_path
        self.reference_path = reference_path

    def on_data(self, item: dict, *args):
        match_val = extract(item, self.reference_path)
        if match_val and match_val in self.kv:
            val = self.kv[match_val]
            fill(item, self.inject_path, val)
        return item


class ConcatFields(JsonIterator):
    """连接数个已有的字段值，形成行的字段。如果目标字段名存在 则覆盖；如果只有一个来源字段，与CopyFields效果相同"""
    def __init__(self, target_key: str, *source_keys, sep: str = '_'):
        super().__init__()
        self.target = target_key
        self.source_keys = source_keys
        self.sep = sep

    def on_data(self, data: dict, *args):
        vals = [str(data.get(k, '')) for k in self.source_keys]
        data[self.target] = self.sep.join(vals)
        return data


class FieldJson(Map):
    """对指定的字符串类型字段转换为json"""
    def __init__(self, key: str):
        super().__init__(self, key)
        assert key is not None, "key should be None"

    def __call__(self, val):
        if isinstance(val, str):
            val = val.replace("'", '"')
            print(val)
            return json.loads(val)
        return val


class FormatFields(Map):
    """对指定字段（为模板字符串）使用指定的值进行填充"""
    def __init__(self, key: str, **kwargs):
        super().__init__(self, key)
        assert key is not None, "key should be None"
        assert len(kwargs) > 0, "**kwargs should not be empty"
        self.values = kwargs

    def __call__(self, val):
        if isinstance(val, str):
            return val.format(**self.values)
        return val

    def __str__(self):
        return f"{self.name}({self.key}, **{self.values})"
