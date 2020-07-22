import os
import re
import sys

from tools import log
from tools import hump
from tools import Dict
from tools import abspath
from tools import dirname
from tools import filetor
from tools import save_pid
from tools import over_func
from tools import time2second
from tools import in_container
from tools import FileDataOperator
from tools import dict_inter_process
from tools import __init__ as init_tools

core: Dict
tools: Dict

_in_container: bool = in_container()
_file = FileDataOperator(dirname(__file__, level=2))
_title: str = hump(os.path.basename(_file.root))

for _name in os.listdir(_file.path.config):
    if _name.endswith('.yml') or _name.endswith('.yaml'):
        _cnf = Dict(filetor(abspath(_file.path.config, _name)) or {})

        _cnf.title, _cnf.file, _cnf.path, _cnf.in_container = \
            _title, _file, _file.path, _in_container

        dict_inter_process(_cnf, lambda k, v: re.findall(
            time2second.pattern.pattern, str(v), re.X) and time2second(v))

        setattr(sys.modules[__name__], _name.split('.')[0], _cnf)

init_tools(tools)

if abspath(sys.argv[0]) == tools.path['go.py']:
    if not _in_container:
        save_pid(abspath(tools.path.log, 'pid'))

    over_func.add(log.logger.info, 'over')
    log.logger.info('start')
