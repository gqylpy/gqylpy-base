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
        def try_except(*a, **kw):
            try:
                return func(*a, **kw)
            except self.exc_type as e:
                if not self.no_log:
                    sign: str = self.mark or tools.hump(func.__name__)
                    exc_name: str = type(e).__name__
                    log.logger.error(f'{sign}.{exc_name}: {e}')

            return self.exc_return

        return try_except


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
        def while_true(*a, **kw):
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

        return while_true


class Retry:

    def __init__(
            self,
            mark: str = None,
            count: int = None,
            cycle: int = 10,
            retry_exc: type = Exception,
    ):
        self.retry_exc = retry_exc
        self.count = count
        self.mark = mark
        self.cycle = cycle

    def __call__(self, func):

        @functools.wraps(func)
        def retry(*a, **kw):
            count = 0

            while True:
                try:
                    return func(*a, **kw)
                except self.retry_exc as e:
                    count += 1

                    sign: str = self.mark or tools.hump(func.__name__)
                    exc_name: str = type(e).__name__

                    log.logger.warning(
                        f'[count:{count}] {sign}.{exc_name}: {e}')

                    if self.count and count == self.count:
                        raise e

                time.sleep(self.cycle)

        return retry


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


retry = Retry
try_except = TryExcept
while_true = WhileTrue
