import os
import json
import yaml

from .dadclass import Dict


def abspath(*a) -> str:
    """Return an absolute path"""
    return os.path.abspath(os.path.join(*a))


def dirname(path: str, level: int = 1) -> str:
    """Culling directories from the
    end according to `level`, usually
    used to get the project root path.
    """
    for n in range(level):
        path = os.path.dirname(os.path.abspath(path))
    return path


def genpath(*a) -> str:
    """Generate path
    Generates a directory based on the passed in value,
    creates it if it does not exist, and returns it.
    """
    dir: str = abspath(*a)
    os.path.exists(dir) or os.makedirs(dir)
    return dir


def filetor(
        file: str,
        data: ... = None,
        tp: 'enum(text, yaml, json)' = None
) -> ...:
    """
    if `data` is None:
        Read file according to `tp`.
    else:
        Write `data` to `file` according to `tp`.
    """
    mode: 'w or r'
    operating: 'Code string'

    if tp is None:
        if file.endswith('yaml') or file.endswith('yml'):
            tp = 'yaml'
        elif file.endswith('json'):
            tp = 'json'
        else:
            tp = 'text'

    if data is None:
        mode = 'r'
        if tp == 'text':
            operating = 'f.read()'
        if tp == 'yaml':
            operating = 'yaml.safe_load(f)'
        if tp == 'json':
            operating = 'json.load(f, *a, **kw)'
    else:
        mode = 'w'
        if tp == 'text':
            operating = 'f.write(str(data))'
        if tp == 'yaml':
            operating = 'yaml.safe_dump(data, f, **kw)'
        if tp == 'json':
            operating = 'json.dump(data, f, *a, **kw)'

    with open(file, mode, encoding='UTF-8') as f:
        return eval(operating)


def fetch_deep_path(
        root: str = None,
        __paths: 'Not param' = None,
        __root: 'Not param' = None
) -> Dict:
    paths = __paths or Dict()
    __root = __root or root

    if root == __root:
        paths['root'] = root

    for name in os.listdir(root):
        full = abspath(root, name)
        paths[full.replace(__root, '')[1:].replace('\\', '/')] = full

        if os.path.isdir(full):
            fetch_deep_path(full, paths, __root)

    return paths


class FileDataOperator:

    def __init__(self, db_dir: str):
        self.root: str = genpath(db_dir)
        self.path: Dict = fetch_deep_path(self.root)

    def __getitem__(self, file):
        full = self.path[file]

        if os.path.isfile(full):
            return filetor(self.path[file])

        return os.listdir(full)

    def __setitem__(self, file, data):
        if file not in self.path:
            self.path[file] = abspath(self.root, file)

        full = self.path[file]

        if not os.path.isdir(os.path.dirname(full)):
            os.makedirs(os.path.dirname(full))

        filetor(full, data)

    def __delitem__(self, file):
        full = self.path.pop(file)

        if os.path.isfile(full):
            os.remove(full)
        else:
            os.removedirs(full)

    def __getattr__(self, file):
        if file in ['root', 'path']:
            return super().__getattribute__(file)
        return self[file]

    def __setattr__(self, file, value):
        if file in ['root', 'path']:
            return super().__setattr__(file, value)
        self[file] = value

    def __delattr__(self, file):
        del self[file]

    def __str__(self):
        return self.root
