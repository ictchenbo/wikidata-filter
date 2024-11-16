from wikidata_filter.iterator.common import Filter
from wikidata_filter.util.jsons import extract


class JsonMatcher(Filter):
    """
    基于JSON数据的规则匹配
    """
    def __init__(self):
        super().__init__(self)
    
    def match(self, row: dict) -> bool:
        return True

    def __call__(self, *args, **kwargs):
        return self.match(args[0])


class SimpleJsonMatcher(JsonMatcher):
    def __init__(self, match_rules: dict = None, **kwargs):
        super().__init__()
        self.match_rules = match_rules or kwargs

    def match(self, row: dict) -> bool:
        for key, value in self.match_rules.items():
            if key not in row or extract(row, key) != value:
                return False
        return True


class JsonPathMatcher(JsonMatcher):
    """
    基于jsonpath的匹配器
    """
    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern
        from jsonpath2.path import Path
        self.p = Path.parse_str(pattern)

    def match(self, row: dict) -> bool:
        for _ in self.p.match(row):
            return True
        return False
