import sys
import json
import threading as th

from pykafka import Topic
from pykafka import Producer
from pykafka import KafkaClient

from . import log
from .dadclass import gdict
from .decorator import retry

__ = sys.modules[__name__]

__default__: Topic


@retry('InitKafka', cycle=60)
def __init__(config: gdict):
    init: gdict = config.kafka.pop('init', {})

    for name, conf in config.kafka.items():

        for item in init.items():
            conf.setdefault(*item)

        client = KafkaClient(**conf)
        topic: Topic = client.topics[name]

        if not hasattr(__, '__default__'):
            setattr(__, '__default__', topic)

        setattr(__, name.replace('-', '_'), topic)


def send(msg: dict, topic: Topic = None):
    """Simple transmitter."""
    pro: Producer = (topic or __default__).get_sync_producer()
    pro.produce(json.dumps(msg).encode())
    log.logger.info(f'Send successfully: {msg}')

    # `pro.stop()` is very slow, so:
    th.Thread(
        target=lambda: pro.stop(),
        daemon=True,
        name='StopProducer'
    ).start()
