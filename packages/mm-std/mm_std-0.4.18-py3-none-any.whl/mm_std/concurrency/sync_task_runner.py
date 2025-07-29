import concurrent
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from mm_std.types_ import Args, Func, Kwargs


class ConcurrentTasks:
    def __init__(self, max_workers: int = 5, timeout: int | None = None, thread_name_prefix: str = "concurrent_tasks") -> None:
        self.max_workers = max_workers
        self.timeout = timeout
        self.thread_name_prefix = thread_name_prefix
        self.tasks: list[ConcurrentTasks.Task] = []
        self.exceptions: dict[str, Exception] = {}
        self.error = False
        self.timeout_error = False
        self.result: dict[str, object] = {}

    @dataclass
    class Task:
        key: str
        func: Func
        args: Args
        kwargs: Kwargs

    def add_task(self, key: str, func: Func, args: Args = (), kwargs: Kwargs | None = None) -> None:
        if kwargs is None:
            kwargs = {}
        self.tasks.append(ConcurrentTasks.Task(key, func, args, kwargs))

    def execute(self) -> None:
        with ThreadPoolExecutor(self.max_workers, thread_name_prefix=self.thread_name_prefix) as executor:
            future_to_key = {executor.submit(task.func, *task.args, **task.kwargs): task.key for task in self.tasks}
            try:
                result_map = concurrent.futures.as_completed(future_to_key, timeout=self.timeout)
                for future in result_map:
                    key = future_to_key[future]
                    try:
                        self.result[key] = future.result()
                    except Exception as err:
                        self.error = True
                        self.exceptions[key] = err
            except concurrent.futures.TimeoutError:
                self.error = True
                self.timeout_error = True
