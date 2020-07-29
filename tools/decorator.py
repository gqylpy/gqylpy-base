import time
import functools

import tools
from . import log


class TryExcept:

    def __init__(
            self,
            except_type: type = Exception,
            mark: str = None,
            no_log: bool = False,
            except_return: ... = None
    ):
        self.mark = mark
        self.no_log = no_log
        self.except_type = except_type
        self.except_return = except_return

    def __call__(self, func):
        @functools.wraps(func)
        def inner(*a, **kw):
            try:
                return func(*a, **kw)
            except self.except_type as e:
                if not self.no_log:
                    sign: str = self.mark or tools.hump(func.__name__)
                    name: str = type(e).__name__
                    log.logger.error(f'{sign}.{name}: {e}')

            return self.except_return

        return inner


class WhileTrue:

    def __init__(
            self,
            cond=True,
            cycle: int = 0,
            before: bool = False
    ):
        self.cond = cond
        self.cycle = cycle
        self.before = before

    def __call__(self, func):
        self.func = func
        return self.inner

    def inner(self, *a, **kw):
        while self.cond:
            if self.before:
                time.sleep(self.cycle)

            ret = self.func(*a, **kw)

            if ret == '_break_':
                break
            if ret == '_continue_':
                continue

            if not self.before:
                time.sleep(self.cycle)


def insure(mark: str = None, cycle: int = 10):
    def wrapper(fn):
        @WhileTrue(cycle=cycle)
        @TryExcept(mark=mark)
        @functools.wraps(fn)
        def inner(*a, **kw):
            fn(*a, **kw)
            return '_break_'

        return inner

    return wrapper


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


try_except = TryExcept
while_true = WhileTrue
