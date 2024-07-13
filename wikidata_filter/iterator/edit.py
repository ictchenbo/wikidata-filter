from wikidata_filter.iterator.base import JsonIterator
from wikidata_filter.util.json_op import extract_val, fill_val


class Select(JsonIterator):
    """
    Select操作
    """
    def __init__(self, *keys):
        super().__init__()
        if keys:
            if isinstance(keys[0], list) or isinstance(keys[0], tuple):
                self.keys = keys[0]
            else:
                self.keys = keys

    def on_data(self, data: dict or None, *args):
        return {key: data.get(key) for key in self.keys}


class Map(JsonIterator):
    """
    Map操作
    """
    def __init__(self, mapper):
        super().__init__()
        self.mapper = mapper

    def on_data(self, data: dict or None, *args):
        return self.mapper(data)


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


class FillField(JsonIterator):
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


class RenameFields(JsonIterator):
    """
    复制字段
    """
    def __init__(self, rename_template: dict[str, str]):
        super().__init__()
        self.rename_template = rename_template

    def on_data(self, data: dict or None, *args):
        for s, t in self.rename_template.items():
            if s in data:
                data[t] = data.pop(s)
        return data


class CopyFields(JsonIterator):
    """
    复制字段
    """
    def __init__(self, copy_template: dict[str, str]):
        super().__init__()
        self.copy_map = copy_template

    def on_data(self, data: dict or None, *args):
        for s, t in self.copy_map.items():
            data[t] = data[s]
        return data


class UpdateFields(JsonIterator):
    """
    更新字段
    """
    def __init__(self, update_template: dict):
        super().__init__()
        self.copy_map = update_template

    def on_data(self, data: dict or None, *args):
        data.update(self.copy_map)
        return data
