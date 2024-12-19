from wikidata_filter.iterator import Map


def load_mod(name: str):
    mod_name = f'wikidata_filter.landinn.{name}'
    mod = __import__(mod_name, fromlist=(mod_name,))
    return mod.calc


class Node(Map):
    """根据提供的模块名称，加载并作为Map的转换函数"""
    def __init__(self, name: str, key: str = None, target_key: str = None):
        super().__init__(load_mod(name), key=key, target_key=target_key)


class Nodes(Map):
    """根据提供的模块名称，加载作为Map的转换函数"""
    def __init__(self, name: str, target_key: str = None):
        super().__init__(load_mod(name), target_key)
