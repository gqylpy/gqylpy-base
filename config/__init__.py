"""https://github.com/gqylpy/gqylpy-base
The code architecture developed by the gqylpy team,
it has unique configuration pattern and a large toolset,
improvements have been under way since the beginning of 2019.
"""
import os
import re
import sys
import tools as gqy

from tools import tm
from tools import log
from tools import file

core: gqy.gdict
tools: gqy.gdict

_in_container: bool = gqy.in_container()
_file = file.FileDataOperator(file.dirname(__file__, level=2))
_db = file.FileDataOperator(_file.path.db)
_title: str = gqy.hump(os.path.basename(_file.root))

for _name in _file.config:
    if _name.endswith('.yml') or _name.endswith('.yaml'):
        __ = gqy.gdict(_file[f'config/{_name}'] or {})

        __.title, __.file, __.db, __.path, __.in_container = \
            _title, _file, _db, _file.path, _in_container

        gqy.dict_inter_process(__, lambda k, v: re.findall(
            tm.Time2Second.pattern.pattern, str(v), re.X
        ) and tm.Time2Second(v))

        setattr(sys.modules[__name__], _name.split('.')[0], __)

gqy.__init__(tools)

if file.abspath(sys.argv[0]) == tools.path['go.py']:
    _file['log/pid'] = os.getpid()

    gqy.add_over_func(log.simple.info, 'over')
    log.simple.info('start')
