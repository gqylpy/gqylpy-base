"""File Operation"""
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
        no_file_return: ... = None,
        type: 'enum(text, yaml, json)' = None,
        encoding: str = 'UTF-8',
        *a, **kw):
    """
    if `data` is None:
        Read file according to `type`.
    else:
        Write `data` to `file` according to `type`.
    """
    mode: 'w or r'
    operating: 'Code string'

    if type is None:
        if file.endswith('yaml') or file.endswith('yml'):
            type = 'yaml'
        elif file.endswith('json'):
            type = 'json'
        else:
            type = 'text'

    if data is None:
        if not os.path.isfile(file):
            return no_file_return
        mode = 'r'
        if type == 'text':
            operating = 'f.read()'
        if type == 'yaml':
            operating = 'yaml.safe_load(f)'
        if type == 'json':
            operating = 'json.load(f, *a, **kw)'
    else:
        mode = 'w'
        if type == 'text':
            operating = 'f.write(str(data))'
        if type == 'yaml':
            operating = 'yaml.safe_dump(data, f, **kw)'
        if type == 'json':
            operating = 'json.dump(data, f, *a, **kw)'

    with open(file, mode, encoding=encoding) as f:
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
