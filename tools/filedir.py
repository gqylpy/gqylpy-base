"""File Operation"""
import os
import json
import yaml
import functools

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
        *a, **kw) -> str or dict:
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
        paths[full.replace(__root, '')[1:].replace(os.sep, '.')] = full

        if os.path.isdir(full):
            fetch_deep_path(full, paths, __root)

    return paths


class FileDataOperator:

    def __init__(self, db_dir: str):
        self.db: str = genpath(db_dir)
        for name, value in fetch_deep_path(db_dir).items():
            if not hasattr(self, name):
                setattr(self, name, value)
            else:
                setattr(self, f'{name}_', value)

    def __getattribute__(self, name: str):
        if name in ['db', 'path', '_FileDataOperator__full_path']:
            return super().__getattribute__(name)

        try:
            return self.__full_path(super().__getattribute__(name))
        except AttributeError:
            return getattr(os.path, name)

    def __full_path(self, func):
        @functools.wraps(func)
        def inner(*a, **kw):
            if a:
                a = list(a)
                a[0] = abspath(self.db, a[0])
            if 'file' in kw:
                kw['file'] = abspath(self.db, kw['file'])

            return func(*a, **kw)

        return inner

    @staticmethod
    def exists(file: str) -> bool:
        return os.path.exists(file)

    def listdir(self):
        return os.listdir(self.db)

    @staticmethod
    def load(file: str, no_file_return=None):
        return filetor(file, no_file_return=no_file_return)

    def save(self, file: str, data: ...):
        if not self.exists(dirname(file)):
            genpath(dirname(file))

        filetor(file, data)

    @staticmethod
    def delete(file: str):

        if os.path.isfile(file):
            os.remove(file)
        else:
            os.removedirs(file)
