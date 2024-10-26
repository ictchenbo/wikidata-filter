from wikidata_filter.iterator.common import Filter


class JsonMatcher(Filter):
    """
    基于JSON数据的规则匹配
    """
    def __init__(self):
        super().__init__(self)
    
    def match(self, row: dict) -> bool:
        pass

    def __call__(self, *args, **kwargs):
        return self.match(args[0])


class SimpleJsonMatcher(JsonMatcher):
    def __init__(self, match_rules: dict):
        super().__init__()
        self.match_relations = match_rules

    def match(self, row: dict) -> bool:
        pass


class JsonPathMatcher(JsonMatcher):
    """
    基于jsonpath的匹配器
    """
    def __init__(self, pattern):
        from jsonpath2.path import Path
        self.p = Path.parse_str(pattern)

    def match(self, row: dict) -> bool:
        for _ in self.p.match(row):
            return True
        return False
