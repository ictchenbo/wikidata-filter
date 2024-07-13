def load_cls(full_name):
    pkg = full_name[:full_name.rfind('.')]
    class_name_only = full_name[full_name.rfind('.') + 1:]
    try:
        mod = __import__(pkg)
    except ImportError:
        raise Exception(f"module [{pkg}] not found!")

    try:
        cls = mod.__getattr__(class_name_only)
    except AttributeError:
        raise Exception(f"class [{class_name_only}] not found in module [{pkg}]!")

    return cls, mod, class_name_only
