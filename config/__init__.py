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

in_container: bool = gqy.in_container()
basedir = file.FileDataOperator(file.dirname(__file__, 2))
db = file.FileDataOperator(basedir.path.db)
title: str = gqy.hump(os.path.basename(basedir.root))

for name in basedir.config:
    if name.endswith('.yml') or name.endswith('.yaml'):
        cnf = gqy.gdict(basedir[f'config/{name}'] or {})

        cnf.db = db
        cnf.title = title
        cnf.basedir = basedir
        cnf.path = basedir.path
        cnf.in_container = in_container

        gqy.dict_inter_process(cnf, lambda k, v: re.findall(
            tm.Time2Second.pattern.pattern, str(v), re.X
        ) and tm.Time2Second(v))

        setattr(sys.modules[__name__], name.split('.')[0], cnf)

gqy.__init__(tools)

if file.abspath(sys.argv[0]) == tools.path['go.py']:
    basedir['log/pid'] = os.getpid()

    gqy.add_over_func(log.simple.info, 'over')
    log.simple.info('start')
