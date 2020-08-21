import os
import time

import multiprocessing as mp

from multiprocessing.pool import Pool
from multiprocessing.pool import AsyncResult


class GQYLPYProcessPool(Pool):

    def __init__(
            self,
            name: str = None,
            processes: int = None,
            *a, **kw
    ):
        name: str = name or 'gqyProcess'
        processes: int = processes or (mp.cpu_count() or 1)

        self.recv_conn, send_conn = mp.Pipe(duplex=False)

        super().__init__(
            processes=processes,
            initializer=self._initializer_,
            initargs=[name, send_conn],
            *a, **kw)

        self.name = name
        self.processes = processes

        self.running = []
        self.results = []
        self.timeout_count = None

    @staticmethod
    def _initializer_(name: str, send_conn):
        send_conn.send(os.getpid())
        mp.current_process().name = name

    def submit(self, func, *a, **kw) -> AsyncResult:
        callback = kw.pop('callback', None)
        error_callback = kw.pop('error_callback', None)

        task: AsyncResult = self.apply_async(
            func=func, args=a, kwds=kw,
            callback=callback,
            error_callback=error_callback)

        task.pid = self.recv_conn.recv()

        self.running.append(task)

        return task

    def block(self, timeout: int = None) -> bool:
        self.results = []
        self.timeout_count = None

        running_length = len(self.running)
        running_last_change_time = time.time()

        while self.running:
            for task, _ in self.running.copy():
                if task.ready():
                    self.running.remove(task)

                    if task.successful():
                        self.results.append(task.get())

            running_length_now = len(self.running)

            if timeout and running_length_now == running_length:
                if time.time() - running_last_change_time > timeout:
                    self.timeout_count = running_length_now

                    for _, pid in self.running:
                        os.kill(pid, 9)

                    return False

            else:
                running_length = running_length_now
                running_last_change_time = time.time()

        return True


ProcessPool = GQYLPYProcessPool
