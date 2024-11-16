from wikidata_filter.iterator.common import Reduce


class Group(Reduce):
    """分组规约，基于指定字段的值进行分组"""
    groups = {}
    return_multiple = True
    last_key = None

    def __init__(self, by: str, emit_fast: bool = True):
        """
        :param by 指定字段的key
        :param emit_fast 是否快速提交数据 如果遇到了不同的键值。默认为True
        """
        super().__init__()
        self.by = by
        self.emit_fast = emit_fast

    def on_data(self, data: dict or None, *args):
        if data is None:
            for key, values in self.groups.items():
                print('grouping key:', key)
                yield dict(key=key, values=values)
            self.groups.clear()
            self.last_key = None
        else:
            group_key = data.get(self.by)
            # print('group_key:', group_key)
            if group_key is None:
                yield None
            group_key = str(group_key)
            if group_key in self.groups:
                self.groups[group_key].append(data)
            else:
                last_v = None
                last_k = self.last_key
                if self.emit_fast and last_k:
                    last_v = self.groups.pop(self.last_key)
                self.last_key = group_key
                self.groups[self.last_key] = [data]
                if last_k:
                    print('grouping key:', last_k)
                    yield dict(key=last_k, values=last_v)

            yield None

    def __str__(self):
        return f"{self.name}(by='{self.by}', emit_fast={self.emit_fast})"
