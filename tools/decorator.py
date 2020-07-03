import time
import functools

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
                    try:
                        log.logger.error(
                            f'{mark or fn.__name__}.{type(e).__name__}: {e}')
                    except Exception as e:
                        print(f'Exception handler error: {type(e).__name__}: {e}')

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
        @functools.wraps(fn)
        @while_true(cycle=cycle)
        @try_except(mark=mark)
        def inner(*a, **kw):
            fn(*a, **kw)
            return '_break_'

        return inner

    return timer
