import os
import re
import sys

from tools import log
from tools import hump
from tools import Dict
from tools import abspath
from tools import dirname
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
_db = FileDataOperator(_file.path.db)
_title: str = hump(os.path.basename(_file.root))

for _name in _file.config:
    if _name.endswith('.yml') or _name.endswith('.yaml'):
        __ = Dict(_file[f'config/{_name}'] or {})

        __.title, __.file, __.db, __.path, __.in_container = \
            _title, _file, _db, _file.path, _in_container

        dict_inter_process(__, lambda k, v: re.findall(
            time2second.pattern.pattern, str(v), re.X) and time2second(v))

        setattr(sys.modules[__name__], _name.split('.')[0], __)

init_tools(tools)

if abspath(sys.argv[0]) == tools.path['go.py']:
    if not _in_container:
        save_pid(abspath(tools.path.log, 'pid'))

    over_func.add(log.logger.info, 'over')
    log.logger.info('start')
