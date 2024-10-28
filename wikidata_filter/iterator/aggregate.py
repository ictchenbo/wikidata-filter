from wikidata_filter.iterator.common import Reduce


class GroupBy(Reduce):
    """分组规约，基于指定字段的值进行分组"""
    last_key = None
    groups: dict = {}

    def __init__(self, key: str, emit_fast: bool = True):
        """
        :param key 指定字段的key
        :param emit_fast 是否快速提交数据 如果遇到了不同的键值。默认为True
        """
        super().__init__()
        self.key = key
        self.emit_fast = emit_fast
        self.return_multiple = True

    def on_data(self, data: dict or None, *args):
        if data is None:
            for item, values in self.groups:
                yield dict(key=item, values=values)
            self.groups.clear()
            self.last_key = None
        else:
            group_key = data.get(self.key)
            if group_key is None:
                yield None
            group_key = str(group_key)
            if group_key in self.groups:
                self.groups[group_key].append(data)
            else:
                last_v = None
                last_k = self.last_key
                if self.emit_fast and self.groups:
                    last_v = self.groups.pop(self.last_key)
                self.last_key = group_key
                self.groups[group_key] = [data]
                yield dict(key=last_k, values=last_v)

            yield None

    def on_complete(self):
        pass
