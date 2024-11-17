def split_path(path: list or str):
    if isinstance(path, str):
        path = path.split('.')
    return path


def extract(val: dict, path: list or str):
    path = split_path(path)
    for key in path:
        if key not in val:
            return None
        val = val[key]
    return val


def fill(target: dict, path: list or str, value):
    path = split_path(path)
    for part in path[:-1]:
        if part not in target:
            target = target[part] = {}
        target = target[part]
    target[path[-1]] = value
