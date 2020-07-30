import sys
import json
import threading as th

from pykafka import Topic
from pykafka import Producer
from pykafka import KafkaClient

from . import log
from .dadclass import Dict
from .decorator import retry

__ = sys.modules[__name__]

__default__: Topic


@retry('InitKafka', cycle=60)
def __init__(config: Dict):
    init: Dict = config.kafka.pop('init', {})

    for name, conf in config.kafka.items():

        for item in init.items():
            conf.setdefault(*item)

        client = KafkaClient(**conf)
        topic: Topic = client.topics[name]

        if not hasattr(__, '__default__'):
            setattr(__, '__default__', topic)

        setattr(__, name.replace('-', '_'), topic)


def send(
        type: str,
        ids: list or str = 'All',
        action: str = None,
        topic: Topic = None):
    """Simple transmitter."""

    # Generate msg.
    msg = Dict()
    msg.type = type
    msg.ids = ids
    if action:
        msg.action = action

    # Send msg.
    pro: Producer = (topic or __default__).get_sync_producer()
    pro.produce(json.dumps(msg).encode())
    log.logger.info(f'kafka.send: {msg}')

    # `pro.stop()` is very slow, so:
    th.Thread(
        target=lambda: pro.stop(),
        daemon=True,
        name='StopProducer'
    ).start()
