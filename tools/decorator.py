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
            return self.try_except(func, *a, **kw)

        return inner

    def try_except(self, func, *a, **kw):
        try:
            return func(*a, **kw)
        except self.exc_type as e:
            if self.no_log:
                return

            mark: str = self.mark or tools.hump(func.__name__)
            exc_name: str = type(e).__name__

            log.decorator.error(f'{mark}.{exc_name}: {e}')
            # tools.aliyun.send_mail(
            #     Subject=f'{mark}.{exc_name}', TextBody=e)

        return self.exc_return


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
            self.while_true(func, *a, **kw)

        return inner

    def while_true(self, func, *a, **kw):
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
        def inner(*a, **kw):
            return self.retry(func, *a, **kw)

        return inner

    def retry(self, func, *a, **kw):
        count = 0

        while True:
            try:
                return func(*a, **kw)
            except self.retry_exc as e:
                count += 1

                sign: str = self.mark or tools.hump(func.__name__)
                exc_name: str = type(e).__name__

                log.decorator.warning(
                    f'[count:{count}] {sign}.{exc_name}: {e}')

                if self.count and count == self.count:
                    raise e

            time.sleep(self.cycle)


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


class TestFuncSpeed:

    def __init__(self, count: int, keep: int = 7):
        self.count = count
        self.keep = keep

    def __call__(self, func):
        self.func = func
        return self.test_func_speed

    def test_func_speed(self, *a, **kw):
        speeds = []

        for _ in range(self.count):
            start = time.time()
            self.func(*a, **kw)
            end = time.time()
            speeds.append(end - start)

        for action in min, max, tools.mean:
            result = round(action(speeds), self.keep)
            print(f'{action.__name__}: {result}')


class RecordDuration:

    def __init__(self, mark: str = None):
        self.mark = mark

    def __call__(self, func):

        @functools.wraps(func)
        def inner(*a, **kw):
            return self.record_duration(func, *a, **kw)

        return inner

    def record_duration(self, func, *a, **kw):
        start = time.time()
        func(*a, **kw)
        end = time.time()

        exec_time: float = round(end - start, 2)
        mark: str = self.mark or tools.hump(func.__name__)

        log.decorator.info(f'{mark}: {exec_time}s')


retry = Retry
try_except = TryExcept
while_true = WhileTrue
record_duration = RecordDuration
