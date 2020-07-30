import os
import sys
import logging

from .dadclass import Dict
from .decorator import retry

__ = sys.modules[__name__]

__default__: logging.getLogger


@retry('InitLog', cycle=60)
def __init__(config: Dict):
    init: Dict = config.log.pop('init', {})

    for name, conf in config.log.items():

        for item in init.items():
            conf.setdefault(*item)

        log = logging.getLogger(name)
        log.setLevel(conf.level)
        formatter = logging.Formatter(conf.logfmt, conf.datefmt)

        if conf.output_method in ['file', 'both']:
            if not os.path.isabs(conf.handler):
                conf.handler = os.path.join(config.path.log, conf.handler)

            if not os.path.exists(os.path.dirname(conf.handler)):
                os.makedirs(os.path.dirname(conf.handler))

            file_handler = logging.FileHandler(conf.handler, encoding='UTF-8')
            file_handler.setFormatter(formatter)
            log.addHandler(file_handler)

        if conf.output_method in ['stream', 'both']:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            log.addHandler(stream_handler)

        # Create pointer in self module.
        setattr(__, name, log)

        # Set the default logger handler.
        if not hasattr(__, '__default__'):
            setattr(__, '__default__', log)


logger: logging.getLogger
