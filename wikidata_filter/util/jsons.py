def extract(val: dict, path: list or str):
    if isinstance(path, str):
        path = path.split('.')
    for key in path:
        if key not in val:
            return None
        val = val[key]
    return val


def fill(target: dict, path: list, value):
    for part in path[:-1]:
        if part not in target:
            target = target[part] = {}
        target = target[part]
    target[path[-1]] = value
