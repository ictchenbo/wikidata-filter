import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def relative_path(path):
    return os.path.join(PROJECT_ROOT, path)
