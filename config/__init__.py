import os
import re
import sys

from tools import log
from tools import Dict
from tools import abspath
from tools import dirname
from tools import filetor
from tools import save_pid
from tools import over_func
from tools import time2second
from tools import in_container
from tools import fetch_deep_path
from tools import FileDataOperator
from tools import dict_inter_process
from tools import __init__ as init_tools

core: Dict
tools: Dict

_in_container: bool = in_container()
_path: Dict = fetch_deep_path(dirname(__file__, level=2))
_title: str = os.path.basename(_path.root)
_file = FileDataOperator(_path.root)

for _name in os.listdir(_path.config):
    if _name.endswith('.yml') or _name.endswith('.yaml'):
        _cnf = Dict(filetor(abspath(_path.config, _name)) or {})

        _cnf.title, _cnf.path, _cnf.file, _cnf.in_container = \
            _title, _path, _file, _in_container

        dict_inter_process(_cnf, lambda k, v: re.findall(
            time2second.pattern.pattern, str(v)) and time2second(v))

        setattr(sys.modules[__name__], _name.split('.')[0], _cnf)

init_tools(tools)

if abspath(sys.argv[0]) == abspath(tools.path.core, 'go.py'):
    if not _in_container:
        save_pid(abspath(tools.path.log, 'pid'))

    over_func.add(log.logger.info, 'over')
    log.logger.info('start')
