import yaml
from wikidata_filter.components import packages, components
from wikidata_filter.util.mod_util import load_cls


class ComponentManager:
    variables: dict = {}

    def find_cls(self, cls_name: str, label: str = 'processor'):
        full_name = self.fullname(cls_name, label)
        if full_name in components:
            return components[full_name]
        cls, mod, class_name = load_cls(full_name)
        components[full_name] = cls
        return cls

    def register_var(self, var_name, var):
        self.variables[var_name] = var

    def fullname(self, cls_name, label: str = 'processor'):
        if '.' in cls_name:
            return f'{packages[label]}.{cls_name}'
        return f'{packages[label]}.{cls_name}'


def init_node(comp_mgr: ComponentManager, expr: str, label: str = 'processor'):
    # get existing node
    if expr in comp_mgr.variables:
        return comp_mgr.variables[expr]

    cls_name = expr

    if '(' in cls_name:
        pos = expr.find('(')
        cls_name = expr[:pos]
        call_part = expr[pos:]
    else:
        call_part = '()'

    cls = comp_mgr.find_cls(cls_name, label=label)
    class_name = cls_name
    if '.' in class_name:
        class_name = class_name[class_name.rfind('.')+1:]

    comp_mgr.register_var(class_name, cls)

    construct = f'{class_name}{call_part}'

    exec(f'__my_node__ = {construct}', globals(), comp_mgr.variables)
    return comp_mgr.variables.get("__my_node__")


def load_flow(flow_file: str, *args, **kwargs) -> tuple:
    flow = yaml.load(open(flow_file, encoding='utf8'), Loader=yaml.FullLoader)
    name = flow.get('name')
    args_num = int(flow.get('arguments', '0'))
    # print(len(args), args_num)
    assert len(args) >= args_num, f"no enough arguments! {args_num} needed!"
    print('loading YAML flow:', name)
    # init context
    comp_mgr = ComponentManager()
    for i in range(len(args)):
        comp_mgr.register_var(f'arg{i+1}', args[i])
    for k, v in kwargs.items():
        comp_mgr.register_var(f'__{k}', v)
    # init nodes
    nodes_def = flow.get('nodes')
    for k, expr in nodes_def.items():
        node = init_node(comp_mgr, expr)
        comp_mgr.register_var(k, node)
    # init loader
    loader = init_node(comp_mgr, flow.get('loader'), label='loader')
    # init processor
    processor = init_node(comp_mgr, flow.get('processor'))

    return loader, processor
