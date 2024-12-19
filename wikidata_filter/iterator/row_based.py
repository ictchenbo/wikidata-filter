from typing import Any

from wikidata_filter.iterator.base import JsonIterator, DictProcessorBase
from wikidata_filter.util.dates import current, current_ts
import uuid


class ReverseKV(DictProcessorBase):
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


class RuleBasedTransform(DictProcessorBase):
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


class AddTS(DictProcessorBase):
    """添加时间戳"""
    def __init__(self, key: str, millis=True):
        self.key = key
        self.millis = millis

    def on_data(self, data: dict, *args):
        data[self.key] = current_ts() if self.millis else current()
        return data


class PrefixID(DictProcessorBase):
    """基于已有字段生成带前缀的ID"""
    def __init__(self, prefix: str, *keys, target_key='_id'):
        self.target_key = target_key
        self.prefix = prefix
        self.keys = keys

    def on_data(self, data: dict, *args):
        parts = [str(data.get(key)) for key in self.keys]
        data[self.target_key] = self.prefix + '_'.join(parts)
        return data


class UUID(DictProcessorBase):
    """"基于UUID生成ID"""
    def __init__(self, target_key='_id'):
        self.target_key = target_key

    def on_data(self, data: dict, *args):
        data[self.target_key] = str(uuid.uuid4())
        return data
