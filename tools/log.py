import os
import sys
import logging

from .dadclass import Dict
from .decorator import retry

__ = sys.modules[__name__]


class Log:

    def __init__(self, name: str, conf: Dict, root: str):
        self.name = name
        self.root = root

        self.level: str = conf.level
        self.output: str = conf.output
        self.handlers: str or list = conf.handlers

        self.log = logging.getLogger(self.name)
        self.formatter = logging.Formatter(conf.logfmt, conf.datefmt)

        self.log.setLevel(self.level)

    def __call__(self):
        if self.output in ['file', 'both']:
            if isinstance(self.handlers, list):
                for handler in self.handlers:
                    self.add_file_handler(handler)
            else:
                self.add_file_handler(self.handlers)

        if self.output in ['stream', 'both']:
            self.add_stream_handler()

        return self.log

    def add_file_handler(self, handler: str):
        if not os.path.isabs(handler):
            handler = os.path.join(self.root, handler)

        if not os.path.exists(os.path.dirname(handler)):
            os.makedirs(os.path.dirname(handler))

        handler = logging.FileHandler(handler, encoding='UTF-8')
        handler.setFormatter(self.formatter)
        self.log.addHandler(handler)

    def add_stream_handler(self):
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        self.log.addHandler(handler)


@retry('InitLog', cycle=60)
def __init__(config: Dict):
    init: Dict = config.log.pop('init', {})

    for name, conf in config.log.items():

        for item in init.items():
            conf.setdefault(*item)

        log = Log(name, conf, config.path.root)()

        setattr(__, name, log)


logger: logging.getLogger
simple: logging.getLogger
