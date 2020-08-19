import time
import functools
import threading as th
import multiprocessing as mp

from multiprocessing.pool import Pool
from multiprocessing.pool import ApplyResult

from . import log
from .time_parser import second2time


class Workers(Pool):

    def __init__(
            self,
            workers: int = None,
            name: str = None,
            job_content=None,
            callback=None,
            error_callback=None,
            *a, **kw):
        name = name or job_content.__name__
        workers = workers or (mp.cpu_count() or 4)

        super().__init__(
            processes=workers,
            initializer=self._set_worker_name,
            initargs=[name],
            *a, **kw)

        self.workers = workers
        self.name = name
        self.job_content = job_content
        self.callback = callback and self._set_callback_name(callback)
        self.error_callback = error_callback and self._set_callback_name(error_callback)

        self.working = []
        self.log = log.logger

        self._start_time = None
        self._reset_start_time = True

    def submit(self, *a, **kw) -> ApplyResult:
        self._reset_start_time_manager()

        worker = self.apply_async(
            func=self.job_content, args=a, kwds=kw,
            callback=self.callback,
            error_callback=self.error_callback)
        self.working.append(worker)

        return worker

    def batch_submit(self, iterable: iter):
        self._reset_start_time_manager()

        worker = self.map_async(
            func=self.job_content,
            iterable=iterable,
            callback=self.callback,
            error_callback=self.error_callback)
        self.working.append(worker)

        return worker

    def wait(self, timeout: int = None) -> str:
        self.log.info(f'Jobs: {self.jobs}, waiting...')
        working_length = len(self.working)
        working_last_change_time = time.time()

        while self.working:
            time.sleep(.2)

            for worker in self.working.copy():
                if worker.ready():
                    self.working.remove(worker)

            working_length_now = len(self.working)

            if timeout and working_length_now == working_length:
                if time.time() - working_last_change_time > timeout:
                    self.log.warning(f'There are {working_length_now} timeouts.')
                    break
            else:
                working_length = working_length_now
                working_last_change_time = time.time()

            self.log.debug(f'Doing: {self.jobs}')

        self._reset_start_time = True
        time_consuming: str = second2time(time.time() - self._start_time)
        self.log.info(f'Work is done, in {time_consuming}')
        return time_consuming

    @property
    def jobs(self) -> int:
        return len(self.working)

    def _reset_start_time_manager(self):
        if self._reset_start_time:
            self._start_time = time.time()
            self._reset_start_time = False

    @staticmethod
    def _set_callback_name(callback_func, name: str = 'Callback'):
        @functools.wraps(callback_func)
        def inner(*a, **kw):
            th.current_thread().name = name
            return callback_func(*a, **kw)

        return inner

    @staticmethod
    def _set_worker_name(name: str):
        mp.current_process().name = name

    @classmethod
    def work_time(cls, func):
        @functools.wraps(func)
        def inner(*a, **kw):
            start = time.time()
            ret = func(*a, **kw)
            end = time.time()
            return ret

        return inner
