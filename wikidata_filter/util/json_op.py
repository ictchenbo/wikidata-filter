def extract_val(val: dict, path: list):
    for key in path:
        if key not in val:
            return None
        val = val[key]
    return val


def fill_val(target: dict, path: list, value):
    for part in path[:-1]:
        if part not in target:
            target = target[part] = {}
        target = target[part]
    target[path[-1]] = value
