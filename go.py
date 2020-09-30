import os
import sys

basedir: str = os.path.dirname(os.path.abspath(__file__))

if basedir not in sys.path:
    sys.path.insert(0, basedir)


import core

if __name__ == '__main__':
    core.run()
