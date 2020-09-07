import abc
import time
import functools

import tools
from . import log


class BaseDecorator(metaclass=abc.ABCMeta):

    def __call__(self, func):
        @functools.wraps(func)
        def inner(*a, **kw):
            return self.core(func, *a, **kw)

        return inner

    @abc.abstractmethod
    def core(self, func, *a, **kw):
        ...


class TryExcept(BaseDecorator):

    def __init__(
            self,
            exc_type: type = Exception,
            mark: str = None,
            ignore: bool = False,
            exc_return: ... = None
    ):
        self.mark = mark
        self.ignore = ignore
        self.exc_type = exc_type
        self.exc_return = exc_return

    def core(self, func, *a, **kw):
        try:
            return func(*a, **kw)
        except self.exc_type as e:
            if not self.ignore:
                try:
                    self.exception_handler(func.__name__, e)
                except Exception as e:
                    print(f'[{int(time.time())}] ExceptionHandlerError: {e}')

        return self.exc_return

    def exception_handler(self, func_name: str, err: Exception):
        mark: str = self.mark or tools.hump(func_name)
        exc_name: str = type(err).__name__

        log.simple.error(f'{mark}.{exc_name}: {str(err)}')

        # tools.aliyun.send_mail(
        #     Subject=f'{mark}.{exc_name}', TextBody=err)


class WhileTrue(BaseDecorator):

    def __init__(
            self,
            cond=True,
            cycle: int = 0,
            before: bool = False
    ):
        self.cond = cond
        self.cycle = cycle
        self.before = before

    def core(self, func, *a, **kw):
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


class Retry(BaseDecorator):

    def __init__(
            self,
            mark: str = None,
            count: int = None,
            cycle: int = 0,
            retry_exc: type = Exception,
    ):
        self.mark = mark
        self.count = count
        self.cycle = cycle
        self.retry_exc = retry_exc

    def core(self, func, *a, **kw):
        count = 0

        while True:
            try:
                return func(*a, **kw)
            except self.retry_exc as e:
                count += 1

                sign: str = self.mark or tools.hump(func.__name__)
                exc_name: str = type(e).__name__

                log.simple.warning(
                    f'[count:{count}/{self.count or "N"}] {sign}.{exc_name}: {e}')

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


class RunTime(BaseDecorator):

    def __init__(self, mark: str = None):
        self.mark = mark

    def core(self, func, *a, **kw):
        start = time.time()
        func(*a, **kw)
        end = time.time()

        mark: str = self.mark or tools.hump(func.__name__)
        exec_time: float = round(end - start, 2)

        log.simple.info(f'{mark}: {exec_time}s')


class TestFuncSpeed(BaseDecorator):

    def __init__(self, count: int, keep: int = 7):
        self.count = count
        self.keep = keep

    def core(self, func, *a, **kw):
        speeds = []

        for _ in range(self.count):
            start = time.time()
            func(*a, **kw)
            end = time.time()
            speeds.append(end - start)

        for action in min, max, tools.mean, sum:
            result = round(action(speeds), self.keep)
            print(f'{action.__name__}: {result}')


retry = Retry
run_time = RunTime
try_except = TryExcept
while_true = WhileTrue
test_func_speed = TestFuncSpeed
