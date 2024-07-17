import yaml
from wikidata_filter.components import components
from wikidata_filter.util.mod_util import load_cls


base_pkg = 'wikidata_filter'
default_mod = 'iterator'


def fullname(cls_name: str, label: str = None):
    if label is not None:
        return f'{base_pkg}.{label}.{cls_name}'
    if '.' in cls_name:
        return f'{base_pkg}.{cls_name}'
    return f'{base_pkg}.{default_mod}.{cls_name}'


def find_cls(full_name: str):
    if full_name in components:
        return components[full_name]
    cls, mod, class_name = load_cls(full_name)
    components[full_name] = cls
    return cls


class ComponentManager:
    variables: dict = {}

    def register_var(self, var_name, var):
        self.variables[var_name] = var

    def init_node(self, expr: str, label: str = None):
        # get existing node
        if expr in self.variables:
            return self.variables[expr]

        cls_name = expr

        if '(' in cls_name:
            pos = expr.find('(')
            cls_name = expr[:pos]
            call_part = expr[pos:]
        else:
            call_part = '()'

        cls = find_cls(fullname(cls_name, label=label))
        class_name = cls_name
        if '.' in class_name:
            class_name = class_name[class_name.rfind('.')+1:]

        self.register_var(class_name, cls)

        construct = f'{class_name}{call_part}'

        exec(f'__my_node__ = {construct}', globals(), self.variables)
        return self.variables.get("__my_node__")


class ProcessFlow:
    comp_mgr = ComponentManager()

    def __init__(self, flow_file: str, *args, **kwargs):
        flow = yaml.load(open(flow_file, encoding='utf8'), Loader=yaml.FullLoader)
        name = flow.get('name')
        args_num = int(flow.get('arguments', '0'))

        # print(len(args), args_num)
        assert len(args) >= args_num, f"no enough arguments! {args_num} needed!"
        print('loading YAML flow:', name)
        # init context
        self.init_base_envs(*args, **kwargs)
        # init consts
        self.init_consts(flow.get('consts') or {})

        # init nodes
        self.init_nodes(flow.get('nodes') or {})

        # init loader
        self.loader = self.comp_mgr.init_node(flow.get('loader'), label='loader')

        # init processor
        self.processor = self.comp_mgr.init_node(flow.get('processor'))

    def init_base_envs(self, *args, **kwargs):
        for i in range(len(args)):
            self.comp_mgr.register_var(f'arg{i + 1}', args[i])
        for k, v in kwargs.items():
            self.comp_mgr.register_var(f'__{k}', v)

    def init_consts(self, consts_def: dict):
        for k, val in consts_def.items():
            self.comp_mgr.register_var(k, val)

    def init_nodes(self, nodes_def: dict):
        for k, expr in nodes_def.items():
            expr = expr.strip()
            if expr.startswith('='):
                node = eval(expr[1:], globals(), self.comp_mgr.variables)
            else:
                node = self.comp_mgr.init_node(expr)
            self.comp_mgr.register_var(k, node)
