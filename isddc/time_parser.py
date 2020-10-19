import re
import time


def stamp2str(
        stamp: int or float = None,
        format: str = '%F %T',
) -> str:
    """timestamp to str time"""
    return time.strftime(format, time.localtime(stamp))


def str2stamp(
        string: str,
        format: str = '%Y-%m-%d %H:%M:%S'
) -> float:
    """str time to timestamp"""
    return time.mktime(time.strptime(string, format))


class Time2Second:
    pattern = re.compile(r'''^
        (?:(\d+(?:\.\d+)?)d)?  # day
        (?:(\d+(?:\.\d+)?)h)?  # hour
        (?:(\d+(?:\.\d+)?)m)?  # minute
        (?:(\d+(?:\.\d+)?)s)?  # second
    $''', flags=re.X)

    one_hour = 60 * 60
    one_day = one_hour * 24

    @classmethod
    def g(cls, x: str):
        return float(x) if x else 0

    def __new__(cls, unit_time: str) -> int or float:
        d, h, m, s = cls.pattern.findall(unit_time.lower())[0]
        d, h, m, s = cls.g(d), cls.g(h), cls.g(m), cls.g(s)
        return cls.one_day * d + cls.one_hour * h + 60 * m + s


def second2time(sec: int or float, x: 'Not param' = '') -> str:
    """Pass in a time in seconds,
    and it will be converted to unit time."""
    if sec < 1:
        return f'{round(sec, 2)}s'

    m, s = divmod(round(sec), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d:
        x += f'{d}d'
    if h:
        x += f'{h}h'
    if m:
        x += f'{m}m'
    if s:
        x += f'{s}s'

    return x


time2second = Time2Second
