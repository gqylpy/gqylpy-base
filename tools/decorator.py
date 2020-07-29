import time
import functools

import tools
from . import log


class TryExcept:

    def __init__(
            self,
            exc_type: type = Exception,
            mark: str = None,
            no_log: bool = False,
            exc_return: ... = None
    ):
        self.mark = mark
        self.no_log = no_log
        self.exc_type = exc_type
        self.exc_return = exc_return

    def __call__(self, func):
        @functools.wraps(func)
        def inner(*a, **kw):
            try:
                return func(*a, **kw)
            except self.exc_type as e:
                if not self.no_log:
                    sign: str = self.mark or tools.hump(func.__name__)
                    exc_name: str = type(e).__name__
                    log.logger.error(f'{sign}.{exc_name}: {e}')

            return self.exc_return

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
        @functools.wraps(func)
        def inner(*a, **kw):
            while self.cond:
                if self.before:
                    time.sleep(self.cycle)

                ret = func(*a, **kw)

                if ret == '_break_':
                    break
                if ret == '_continue_':
                    continue

                if not self.before:
                    time.sleep(self.cycle)

        return inner


class Retry:

    def __init__(
            self,
            retry_exc: type = Exception,
            retry_count: int = None,
            cycle: int = 10,
            mark: str = None
    ):
        self.retry_exc = retry_exc
        self.retry_count = retry_count
        self.mark = mark
        self.cycle = cycle
        self.count = 0

    def __call__(self, func):
        sign: str = self.mark or tools.hump(func.__name__)

        @while_true(cycle=self.cycle)
        @functools.wraps(func)
        def wrapper(*a, **kw):
            try:
                func(*a, **kw)
            except self.retry_exc as e:
                self.count += 1
                exc_name: str = type(e).__name__
                msg = f'[retry:{self.count}] {sign}.{exc_name}: {e}'

                if self.retry_count and self.count < self.retry_count:
                    log.logger.warning(msg)
                    return

                log.logger.error(msg)

            return '_break_'

        return wrapper


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
