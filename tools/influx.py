import sys

from influxdb import InfluxDBClient

from . import over_func
from .dadclass import Dict
from .decorator import retry

__ = sys.modules[__name__]

__default__: InfluxDBClient


@retry('InitInflux', cycle=60)
def __init__(config: Dict):
    influx: Dict = config.influx
    init: Dict = influx.pop('init', {})

    for name, conf in influx.items():

        for item in init.items():
            conf.setdefault(*item)

        client = InfluxDBClient(**conf)

        over_func.add(client.close)

        setattr(__, name, client)

        if not hasattr(__, '__default__'):
            setattr(__, '__default__', client)


def query(
        sql: str,
        one: bool = False,
        epoch: str = None,
        datastyle: 'enum(dict, list)' = dict,
        client: InfluxDBClient = None,
        *a, **kw) -> list or dict:
    """
    Encapsulate the 'InfluxDBClient.query' method.

    Help:
        Turn off the highlighting of the PyCharm SQL
        statement: `File -> Editor -> Inspections -> SQL`

    :param one: Returns a piece of data.
    :param epoch: The time format.
    :param datastyle: The data type returned, dict or str
    :param client: Specified database, the default is `__default__`.
    """
    queryset = (client or __default__).query(sql, epoch=epoch, *a, **kw)

    if not queryset:
        return {} if datastyle is dict and one else []

    if datastyle is dict:
        data = Dict([[dict(
            (qst['columns'][i], val[i])
            for i in range(len(val)))
            for val in qst['values']]
            for qst in queryset.raw['series']])
        # uuid: str = qst.tags.uuid
    else:
        data = [series['values'] for series in queryset.raw['series']]

    if 'GROUP BY' not in sql:
        data = data[0]

    return data[0] if one else data


def write_points(data: list, client: InfluxDBClient = None, *a, **kw):
    """Encapsulate the 'InfluxDBClient.write_points' method"""
    return (client or __default__).write_points(data, *a, **kw)


mon: InfluxDBClient
