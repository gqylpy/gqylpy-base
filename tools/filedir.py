import os
import yaml
import json

from .dadclass import gdict


class FileDataOperator:

    def __init__(self, db_dir: str):
        self.root: str = genpath(db_dir)
        self.path: gdict = fetch_deep_path(self.root)

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


class Filetor:
    """
    if `data` is None:
        Read file according to `ftype`.
    else:
        Write `data` to `file` according to `ftype`.
    """

    def __new__(
            cls,
            file: str,
            data=None,
            ftype: 'enum(json, yaml, text)' = None
    ):
        mode = 'r' if data is None else 'w'

        if ftype is None:
            ftype: str = file.split('.')[-1]

        process_func = f'_for_{ftype}_'

        with open(file, mode, encoding='UTF-8') as fp:
            if hasattr(cls, process_func):
                return getattr(cls, process_func)(fp, data)

            return cls._for_text_(fp, data)

    @classmethod
    def _for_json_(cls, fp: open, data=None):
        if data is None:
            return json.load(fp)

        json.dump(data, fp)

    @classmethod
    def _for_yaml_(cls, fp: open, data=None):
        if data is None:
            return yaml.safe_load(fp)

        return yaml.safe_dump(data, fp)

    @classmethod
    def _for_text_(cls, fp: open, data=None):
        if data is None:
            return fp.read()

        return fp.write(str(data))

    _for_yml_ = _for_yaml_
    _for_txt_ = _for_text_


def fetch_deep_path(
        root: str = None,
        _paths: 'Not param' = None,
        _root: 'Not param' = None
) -> gdict:
    paths = _paths or gdict()
    _root = _root or root

    if root == _root:
        paths['root'] = root

    for name in os.listdir(root):
        full = abspath(root, name)
        paths[full.replace(_root, '')[1:].replace('\\', '/')] = full

        if os.path.isdir(full):
            fetch_deep_path(full, paths, _root)

    return paths


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


filetor = Filetor
