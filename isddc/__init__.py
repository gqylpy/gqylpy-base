import os
import re
import sys
import copy
import hashlib
import subprocess
import collections

from . import log
from . import kube
from . import pool
from . import kafka
from . import mongo
from . import mysql
from . import influx
from . import aliyun
from . import crypto
from . import dbpool
from . import over_func
from . import secure_shell
from . import filedir as file
from . import dadclass as base
from . import decorator as dec
from . import time_parser as tm

from .over_func import add_over_func

from .pool import ProcessPool
from .secure_shell import SecureShell

from .crypto import encrypt
from .crypto import decrypt

from .dadclass import gdict
from .dadclass import DictMode
from .dadclass import SingletonMode

from .time_parser import str2stamp
from .time_parser import stamp2str
from .time_parser import time2second
from .time_parser import second2time

from .decorator import retry
from .decorator import run_time
from .decorator import try_except
from .decorator import while_true
from .decorator import after_func
from .decorator import before_func
from .decorator import test_func_speed

from .filedir import filetor
from .filedir import abspath
from .filedir import dirname
from .filedir import genpath
from .filedir import fetch_deep_path
from .filedir import FileDataOperator


@retry('InitTools', cycle=10)
def __init__(config: gdict):
    config = copy.deepcopy(config)

    for name in config:
        try:
            load_name(f'{__name__}.{name}.__init__')(config)
        except (ModuleNotFoundError, AttributeError):
            pass


@retry(count=3, cycle=0.3)
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


def cmd_list_to_dict(
        cmd_list: str,
        split: str = None
) -> list:
    """Used to turn the command output result with a title
    into a dictionary, such as `kubectl get pod`."""
    result = [[value.strip() for value in line.split(split)]
              for line in cmd_list.splitlines()]
    keys = [key.lower() for key in result[0]]
    return [dict(zip(keys, values)) for values in result[1:]]


def prt(*args, color: int = 31, font: int = 0,
        end: str = '\n', sep: str = ' ', file: open = None):
    """
    Custom print font and color.

    Color:
        31-red 32-green 34-blue 37-Gray 38-black
    Font:
        0-normal 1-bold
    sep:
        string inserted between values, default a space.
    """
    info: str = sep.join(str(i) for i in args)
    format: str = f'\033[{font};{color};0m{info}\033[0m'
    print(format, end=end, file=file)


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


class Response(gdict):
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
    if '_' in name:
        name: str = ''.join(_.capitalize() for _ in name.split('_'))

    if '-' in name:
        name: str = ''.join(_.capitalize() for _ in name.split('-'))

    return name[0].upper() + name[1:]


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


def mean(numbers: list) -> float:
    result = 0

    for num in numbers:
        result += num

    return result / len(numbers)
