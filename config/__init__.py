"""https://github.com/idclpy/idclpy-base
The code architecture developed by the idclpy team,
it has unique configuration pattern and a large toolset,
improvements have been under way since the beginning of 2019.
"""
import os
import re
import sys
import isddc as idc

from isddc import tm
from isddc import log
from isddc import file

core: idc.gdict
isddc: idc.gdict

in_container: bool = idc.in_container()
basedir = file.FileDataOperator(file.dirname(__file__, 2))
db = file.FileDataOperator(basedir.path.db)
title: str = idc.hump(os.path.basename(basedir.root))

for name in basedir.config:
    if name.endswith('.yml') or name.endswith('.yaml'):
        cnf = idc.gdict(basedir[f'config/{name}'] or {})

        cnf.db = db
        cnf.title = title
        cnf.basedir = basedir
        cnf.path = basedir.path
        cnf.in_container = in_container

        idc.dict_inter_process(cnf, lambda k, v: re.findall(
            tm.Time2Second.pattern.pattern, str(v), re.X
        ) and tm.Time2Second(v))

        setattr(sys.modules[__name__], name.split('.')[0], cnf)

idc.__init__(isddc)

if file.abspath(sys.argv[0]) == isddc.path['go.py']:
    basedir['log/pid'] = os.getpid()

    idc.add_over_func(log.simple.info, 'over')
    log.simple.info('start')
