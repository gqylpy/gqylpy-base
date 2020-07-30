import os
import re
import sys
import copy
import hashlib
import subprocess
import collections

from . import log
from . import mongo
from . import kafka
from . import mysql
from . import influx
from . import dbpool
from . import aliyun
from . import over_func

from .workers import Workers
from .secure_shell import SecureShell

from .crypto import encrypt
from .crypto import decrypt

from .dadclass import Dict
from .dadclass import SingletonMode

from .time_process import str2stamp
from .time_process import stamp2str
from .time_process import time2second
from .time_process import second2time

from .decorator import retry
from .decorator import try_except
from .decorator import while_true
from .decorator import after_func
from .decorator import before_func

from .filedir import abspath
from .filedir import dirname
from .filedir import genpath
from .filedir import filetor
from .filedir import fetch_deep_path
from .filedir import FileDataOperator


@retry('InitTools', cycle=10)
def __init__(config: Dict):
    config = copy.deepcopy(config)

    for name in config:
        if name in globals() and hasattr(globals()[name], '__init__'):
            globals()[name].__init__(config)


def exec_cmd(cmd: str) -> str:
    """
    if exec the cmd success:
        return result
    else:
        throw exception
    """
    status, output = subprocess.getstatusoutput(cmd)
    assert status == 0, f'{cmd}: {output}'
    return output


def save_pid(file: str):
    """Save the main program id to file"""
    filetor(file, os.getpid())


def prt(*args, color: int = 31, font: int = 0,
        end: str = '\n', sep: str = ' ', file: open = None):
    """
    Custom Print Font and Color.

    Color:
        31-red 32-green 34-blue 37-Gray 38-black
    Font:
        0-normal 1-bold
    sep:
        string inserted between values, default a space.
    """
    print(
        f'\033[{font};{color};0m{sep.join(str(i) for i in args)}\033[0m',
        end=end, file=file)


class md5:

    def __init__(self, *a, **kw):
        self.m5 = hashlib.md5(*a, **kw)

    def __new__(cls, data: str = None, *a, **kw):
        """Returns the encrypted string directly"""
        if data is None:
            return object.__new__(cls)

        m5 = cls(*a, **kw)
        m5.update(data)
        return m5.hexdigest

    def update(self, data):
        if isinstance(data, str):
            data = data.encode('UTF-8')

        if not isinstance(data, (str, bytes)):
            data = str(data).encode('UTF-8')

        self.m5.update(data)

    def update_str(self, data: str):
        self.m5.update(data.encode('UTF-8'))

    @property
    def hexdigest(self) -> str:
        return self.m5.hexdigest()


class Response(Dict):
    """API Response"""

    def __init__(
            self, code: int = 200,
            data: dict = None,
            msg: str = 'ok'):
        self.code = code
        self.data = data or {}
        self.msg = msg


def dict_inter_process(data: dict, func=None) -> dict:
    """Dictionary internal processing
    Used to batch process values inside a dictionary.
    :param data: A dict.
    :param func: Your handler functions, ps:
        def func(name, value):
            if name == 'xxx':
                return process(value)
    """

    def one(data: dict):
        for name, value in data.items():
            data[name] = two(name, value)

        return data

    def two(name=None, value={}):
        value = func(name, value) or value

        if isinstance(value, dict):
            return one(value)

        if isinstance(value, collections.Iterable) \
                and not isinstance(value, str):
            return [two(value=v) for v in value]

        return value

    return one(data)


def in_container() -> bool:
    """Whether to run in the container."""
    if os.name == 'posix':

        if exec_cmd('fdisk -l'):
            return False

        return True

    return False


def load_module(module: str):
    __import__(module)
    return sys.modules[module]


def load_name(name: str):
    module, _, name = name.rpartition('.')
    module = load_module(module)
    return getattr(module, name)


def load_object(class_path: str, *a, **kw):
    return load_name(class_path)(*a, **kw)


def hump(name: str) -> str:
    return ''.join(_.capitalize() for _ in name.split('_'))


def underline(name: str) -> str:
    for _ in re.findall(r'([A-Z]+)[A-Z]', name):
        name = name.replace(_, _.capitalize())

    result: list = re.findall(r'[A-Z][a-z]+|[A-Z]\d', name)

    return '_'.join(_.lower() for _ in result)


def get_caller(level: int = 1) -> str:
    back = sys._getframe().f_back

    for _ in range(level):
        back = back.f_back

    return back.f_code.co_name
