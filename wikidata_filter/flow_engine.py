import os
import yaml

from wikidata_filter.base import relative_path
from wikidata_filter.components import components
from wikidata_filter.util.mod_util import load_cls


base_pkg = 'wikidata_filter'
default_mod = 'iterator'


def fullname(cls_name: str, label: str = None):
    """
    基于对象短名生成全限定名 如`database.mongodb.MongoLoader` -> `wikidata_filter.loader.database.mongodb.MongoLoader`
    如果该对象在模块中引入，则可以简化，如`database.MongoLoader` -> `wikidata_filter.loader.database.MongoLoader`

    如果指定了label参数，则从对应的子模块（如loader、iterator、util）查找 否则根据cls_name查找
    如果cls_name包含模块路径，则尝试从`wikidata_filter.`开始查找
    否则从在iterator模块下查找

    如果label未指定，则根据cls_name查找对应iterator的写法

    :param cls_name 算子构造器名字（类名或函数名）
    :param label 指定子模块的标签（loader/iterator/matcher）
    """
    if label is not None:
        # 兼容两种情况 loader/iterator
        if cls_name.startswith(f'{label}.'):
            return f'{base_pkg}.{cls_name}'
        return f'{base_pkg}.{label}.{cls_name}'
    if '.' in cls_name:
        # wikidata_filter下面的其他模块 如util
        path = relative_path(f'{base_pkg}/{cls_name.split(".")[0]}')
        if os.path.exists(path):
            return f'{base_pkg}.{cls_name}'
    # 默认模块下 -> wikidata_filter/iterator/__init__
    return f'{base_pkg}.{default_mod}.{cls_name}'


def find_cls(full_name: str):
    """
    根据对象的全限定名加载对象 提前加载到`components`中可提高加载速度
    """
    if full_name in components:
        return components[full_name]
    cls, mod, class_name = load_cls(full_name)
    # 缓存对象
    components[full_name] = cls
    return cls


class ComponentManager:
    variables: dict = {}

    def register_var(self, var_name, var):
        self.variables[var_name] = var

    def is_reference_node(self, expr: str):
        """简单判断策略 如果不包含点、全部为小写、在变量中则认为是"""
        if expr in self.variables and '.' not in expr and expr.islower():
            return True
        return False

    def init_node(self, expr: str, label: str = None):
        if not expr:
            return None

        if expr.startswith('='):
            return eval(expr[1:], globals(), self.variables)

        # 支持在loader/processor定义中直接引用nodes中定义的节点
        if self.is_reference_node(expr):
            return self.variables[expr]

        # split expr into constructor and call_part
        constructor = expr
        if '(' in constructor:
            pos = expr.find('(')
            constructor = expr[:pos]
            call_part = expr[pos:]
        else:
            call_part = '()'
        assert call_part.endswith(')'), f"Invalid node expr: {expr}, should be a function call"
        # get short class name from constructor
        class_name = constructor
        if '.' in class_name:
            class_name = class_name[class_name.rfind('.')+1:]
        class_name_full = fullname(constructor, label=label)
        # find constructor object
        cls = find_cls(class_name_full)
        # register for later use
        # eval虽然简单，但是存在限制：由于Python语法限制，必须使用组件短名
        # 不同构造器的短名如果相同 则会替换已有的构造器
        self.register_var(class_name, cls)
        new_node = eval(f'{class_name}{call_part}', globals(), self.variables)
        return new_node


class ProcessFlow:
    comp_mgr = ComponentManager()

    def __init__(self, flow_file: str, *args, **kwargs):
        flow = yaml.load(open(flow_file, encoding='utf8'), Loader=yaml.FullLoader)
        self.name = flow.get('name')
        args_num = int(flow.get('arguments', '0'))

        # print(len(args), args_num)
        assert len(args) >= args_num, f"no enough arguments! {args_num} needed!"
        # init context
        self.init_base_envs(*args, **kwargs)
        # init consts
        self.init_consts(flow.get('consts') or {})

        # init nodes
        self.init_nodes(flow.get('nodes') or {})

        # init loader, maybe None
        self.loader = self.comp_mgr.init_node(flow.get('loader'), label='loader')

        # init processor, maybe None
        self.processor = self.comp_mgr.init_node(flow.get('processor'), label='iterator')

        self.end_signal = flow.get("finish_signal") is True

    def init_base_envs(self, *args, **kwargs):
        for i in range(len(args)):
            self.comp_mgr.register_var(f'arg{i + 1}', args[i])
        for k, v in kwargs.items():
            self.comp_mgr.register_var(f'__{k}', v)

    def init_consts(self, consts_def: dict):
        for k, val in consts_def.items():
            if isinstance(val, str) and val.startswith("$"):
                # consts的字符串变量如果以$开头 则获取环境变量
                val = os.environ.get(val[1:])
            self.comp_mgr.register_var(k, val)

    def init_nodes(self, nodes_def: dict):
        """初始化节点 支持普通节点、loader节点和非流程节点"""
        for k, expr in nodes_def.items():
            expr = expr.strip()

            # 特殊逻辑 支持nodes中初始化loader组件
            label = None
            if k.startswith("loader"):
                label = "loader"

            node = self.comp_mgr.init_node(expr, label=label)
            self.comp_mgr.register_var(k, node)
            # print(k, expr, node, id(node))
