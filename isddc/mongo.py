import sys

from pymongo import MongoClient
from pymongo.database import Database

from . import over_func
from .dadclass import gdict
from .decorator import retry


@retry('InitMongo', cycle=60)
def __init__(config: gdict):
    init: gdict = config.mongo.pop('init', {})

    for name, conf in config.mongo.items():
        db: str = conf.pop('db', name)

        for item in init.items():
            conf.setdefault(item)

        client = MongoClient(**conf)

        over_func.add(client.close)

        setattr(sys.modules[__name__], name, client[db])


mon: Database
