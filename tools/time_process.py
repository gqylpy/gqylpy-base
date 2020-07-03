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


class time2second:
    pattern = re.compile(
        r'^'
        r'(?:(\d+(?:\.\d+)?)d)?'  # day
        r'(?:(\d+(?:\.\d+)?)h)?'  # hour
        r'(?:(\d+(?:\.\d+)?)m)?'  # minute
        r'(?:(\d+(?:\.\d+)?)s)?'  # second
        r'$')

    one_hour = 60 * 60
    one_day = one_hour * 24

    def __new__(cls, unit_time: str):
        x = cls.pattern.findall(unit_time)[0]

        d = float(x[0] or 0)
        h = float(x[1] or 0)
        m = float(x[2] or 0)
        s = float(x[3] or 0)

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
