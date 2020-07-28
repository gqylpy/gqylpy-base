import time
import functools

import tools
from . import log


def try_except(
        except_type: type = Exception,
        mark: str = None,
        no_log: bool = False,
        except_return: ... = None
):
    def timer(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            try:
                return fn(*a, **kw)
            except except_type as e:
                if not no_log:
                    sign: str = mark or tools.hump(fn.__name__)
                    name: str = type(e).__name__
                    log.logger.error(f'{sign}.{name}: {e}')

            return except_return

        return inner

    return timer


def while_true(cond=True, cycle: int = 0, before: bool = False):
    def timer(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            while cond:
                before and time.sleep(cycle)
                ret = fn(*a, **kw)
                if ret == '_break_':
                    break
                if ret == '_continue_':
                    continue
                before or time.sleep(cycle)

        return inner

    return timer


def insure(mark: str = None, cycle: int = 10):
    def timer(fn):
        @while_true(cycle=cycle)
        @try_except(mark=mark)
        @functools.wraps(fn)
        def inner(*a, **kw):
            fn(*a, **kw)
            return '_break_'

        return inner

    return timer


def before_func(func=None):
    def timer(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            ret = func(*a, **kw)

            if ret:
                return fn(ret)
            else:
                return fn(*a, **kw)

        return inner

    return timer


def after_func(func=None, independent: bool = False):
    def timer(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            ret = fn(*a, **kw)

            if independent:
                func()
                return ret
            else:
                return func(ret)

        return inner

    return timer
