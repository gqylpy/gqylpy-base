import os
import time

import threading as th
import multiprocessing as mp

from multiprocessing.pool import Pool
from multiprocessing.pool import AsyncResult


class GQYLPYBatchProcessPool(Pool):

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

        self.running = {}

    @staticmethod
    def _initializer_(name: str, send_conn):
        pid: int = os.getpid()
        # send_conn.send(pid)
        mp.current_process().name = name + str(pid)

    def submit(self, func, *a, **kw) -> AsyncResult:
        callback = kw.pop('callback', None)
        error_callback = kw.pop('error_callback', None)

        task: AsyncResult = self.apply_async(
            func=func, args=a, kwds=kw,
            callback=callback,
            error_callback=error_callback)

        # task.pid = self.recv_conn.recv()

        self.running.setdefault(self.thread_name, []).append(task)

        return task

    def block(
            self,
            timeout: int or float = None,
            cycle: int or float = .1
    ) -> list:
        thread_name: str = self.thread_name

        if thread_name not in self.running:
            return []

        running: list = self.running[thread_name]
        results = []

        running_length = len(running)
        running_last_change_time = time.time()

        while running:
            time.sleep(cycle)

            for task in running.copy():
                if task.ready():
                    running.remove(task)

                    if task.successful() and task.get():
                        results.append(task.get())

            running_length_now = len(running)

            if timeout and running_length_now == running_length:
                if time.time() - running_last_change_time > timeout:
                    # for task in running:
                    #     os.kill(task.pid, 9)

                    running.clear()
                    break

            else:
                running_length = running_length_now
                running_last_change_time = time.time()

        return results

    @property
    def thread_name(self) -> str:
        return th.current_thread().name


BatchProcessPool = GQYLPYBatchProcessPool
