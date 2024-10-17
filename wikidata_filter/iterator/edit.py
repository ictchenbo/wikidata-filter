import json

from wikidata_filter.iterator.base import JsonIterator
from wikidata_filter.util.json_op import extract_val, fill_val
from wikidata_filter.iterator.common import Reduce


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


class SelectVal(JsonIterator):
    """
    Select操作
    """
    def __init__(self, key):
        super().__init__()
        self.key = key

    def on_data(self, data: dict or None, *args):
        return data.get(self.key)


class Map(JsonIterator):
    """
    Map操作
    """
    def __init__(self, mapper):
        super().__init__()
        self.mapper = mapper

    def on_data(self, data: dict or None, *args):
        return self.mapper(data)


class Flat(JsonIterator):
    def __init__(self):
        self.return_multiple = True

    def on_data(self, data, *args):
        if isinstance(data, list) or isinstance(data, tuple):
            # print('Flat', data)
            for item in data:
                yield item
        else:
            yield data


class FlatMap(Flat):
    """
    Map操作
    """
    def __init__(self, mapper):
        super().__init__()
        self.mapper = mapper

    def on_data(self, data: dict or None, *args):
        val = self.mapper(data)
        return super().on_data(val)


class FieldJson(JsonIterator):
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
    def __init__(self, **kwargs):
        self.adds = kwargs or {}

    def on_data(self, data, *args):
        for k, v in self.adds.items():
            if k not in data:
                data[k] = v
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


class RenameFields(JsonIterator):
    """
    复制字段
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.rename_template = kwargs

    def on_data(self, data: dict or None, *args):
        for s, t in self.rename_template.items():
            if s in data:
                data[t] = data.pop(s)
        return data


class UpdateFields(JsonIterator):
    """
    复制字段
    """
    def __init__(self, other: dict):
        super().__init__()
        self.that = other

    def on_data(self, data: dict or None, *args):
        for s, t in self.that.items():
            data[t] = data[s]
        return data


class ReverseKV(JsonIterator):
    """
    对调字典的字段名和字段值
    """
    def on_data(self, data: dict, *args):
        return {v: k for k, v in data.items()}


def get_field_value(field):
    def get_value(row):
        return row.get(field)

    return get_value


def parse_field(field):
    if isinstance(field, str) and field.startswith('@'):
        return get_field_value(field[1:])
    return lambda _: field


def parse_rules(rules):
    rule_map = {}
    for rule in rules:
        target = rule
        source = None
        if ":" in rule:
            pos = rule.find(":")
            target = rule[:pos]
            source = rule[pos + 1]
        source = source or ("@" + target)
        rule_map[target] = parse_field(source)

    return rule_map


class RuleBasedTransform(JsonIterator):
    """
    基于规则的数据转换 规则定义：
        - "f1:123,f2:@t1,..."
        - ["f1:123", "f2:@t1", ... ]
        - {"f1": 123, "f2": "@t1", ... ]
    其中 "@t1" 表示引用原始数据t1字段 其他情况则为字面值
    """
    def __init__(self, rules: list or str):
        if isinstance(rules, str):
            self.rule_map = parse_rules(rules.split(","))
        elif isinstance(rules, list):
            self.rule_map = parse_rules(rules)
        elif isinstance(rules, dict):
            self.rule_map = {}
            for target, s in rules.items():
                self.rule_map[target] = parse_field(s)

    def on_data(self, data: dict, *args):
        ret = {}
        for t, sFun in self.rule_map.items():
            res = sFun(data)
            if res is not None:
                ret[t] = res
        return ret


class GroupBy(Reduce):
    """分组规约"""
    last_key = None
    groups: dict = {}

    def __init__(self, by: str, emit_fast: bool = True):
        super().__init__()
        self.by = by
        self.fast = emit_fast
        self.return_multiple = True

    def on_data(self, data: dict or None, *args):
        if data is None:
            for item, values in self.groups:
                yield dict(key=item, values=values)
            self.groups.clear()
            self.last_key = None
        else:
            group_key = data.get(self.by)
            if group_key is None:
                yield None
            group_key = str(group_key)
            if group_key in self.groups:
                self.groups[group_key].append(data)
            else:
                last_v = None
                last_k = self.last_key
                if self.fast and self.groups:
                    last_v = self.groups.pop(self.last_key)
                self.last_key = group_key
                self.groups[group_key] = [data]
                yield dict(key=last_k, values=last_v)

            yield None

    def on_complete(self):
        pass
