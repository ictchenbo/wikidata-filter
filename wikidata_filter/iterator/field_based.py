import json
from wikidata_filter.iterator.base import JsonIterator
from wikidata_filter.util.json_op import extract_val, fill_val


class Select(JsonIterator):
    """
    Select操作 key支持嵌套，如`user.name`表示user字段下面的name字段 并将name作为结果字段名
    """
    def __init__(self, *keys):
        super().__init__()
        if keys:
            if isinstance(keys[0], list) or isinstance(keys[0], tuple):
                self.keys = keys[0]
            else:
                self.keys = keys
        self.path = {}
        for key in self.keys:
            path = key.split('.')
            self.path[key] = path

    def on_data(self, data: dict or None, *args):
        return {key: extract_val(data, path) for key, path in self.path.items()}


class SelectVal(JsonIterator):
    """
    Select操作
    """
    def __init__(self, key):
        super().__init__()
        self.key = key

    def on_data(self, data: dict or None, *args):
        return data.get(self.key)


class FieldJson(JsonIterator):
    """对指定的字符串类型字段转换为json"""
    def __init__(self, key: str):
        self.key = key

    def on_data(self, data: dict or None, *args):
        if data and data.get(self.key):
            val = data[self.key]
            if isinstance(val, str):
                val = val.replace("'", '"')
                print(val)
                data[self.key] = json.loads(val)
        return data


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

    def on_data(self, data: dict or None, *args):
        return {k: v for k, v in data.items() if k not in self.keys}


class AddFields(JsonIterator):
    """添加字段 如果不存在"""
    def __init__(self, **kwargs):
        self.adds = kwargs or {}

    def on_data(self, data, *args):
        for k, v in self.adds.items():
            if k not in data:
                data[k] = v
        return data


class RenameFields(JsonIterator):
    """对字段重命名"""
    def __init__(self, **kwargs):
        super().__init__()
        self.rename_template = kwargs

    def on_data(self, data: dict or None, *args):
        for s, t in self.rename_template.items():
            if s in data:
                data[t] = data.pop(s)
        return data


class UpdateFields(JsonIterator):
    """更新字段，Upsert模式"""
    def __init__(self, other: dict):
        super().__init__()
        self.that = other

    def on_data(self, data: dict or None, *args):
        for s, t in self.that.items():
            data[t] = data[s]
        return data


class CopyFields(JsonIterator):
    """复制已有的字段 如果目标字段名存在 则覆盖"""
    def __init__(self, **kwargs):
        super().__init__()
        self.copy_template = kwargs

    def on_data(self, data: dict or None, *args):
        for s, t in self.copy_template.items():
            data[t] = data.get(s)
        return data


class InjectField(JsonIterator):
    """
    基于给定的KV缓存 对当前数据进行填充
    """
    def __init__(self, kv: dict, inject_path: str or list, reference_path: str):
        if isinstance(inject_path, str):
            inject_path = inject_path.split('.')
        if isinstance(reference_path, str):
            reference_path = reference_path.split('.')

        self.kv = kv
        self.inject_path = inject_path
        self.reference_path = reference_path

    def on_data(self, item: dict or None, *args):
        match_val = extract_val(item, self.reference_path)
        if match_val and match_val in self.kv:
            val = self.kv[match_val]
            fill_val(item, self.inject_path, val)
        return item


class ConcatFields(JsonIterator):
    """连接数个已有的字段值，形成行的字段。如果目标字段名存在 则覆盖；如果只有一个来源字段，与CopyFields效果相同"""
    def __init__(self, target_key: str, *source_keys, sep: str = '_'):
        super().__init__()
        self.target = target_key
        self.source_keys = source_keys
        self.sep = sep

    def on_data(self, data: dict or None, *args):
        vals = [str(data.get(k, '')) for k in self.source_keys]
        data[self.target] = self.sep.join(vals)
        return data
