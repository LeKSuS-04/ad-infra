import threading
from collections.abc import Callable
from functools import wraps

from .logger import log
from .syncher import Syncer
from .syncher.resources import Resource


class TaskManager:
    def __init__(self):
        self.tasks: list[threading.Thread] = []

    def add_tasks(self, tasks: list[Callable]):
        for task in tasks:
            process = threading.Thread(target=task, name=task.__name__)
            process.start()
            self.tasks.append(process)

    def wait_until_all_finished(self):
        for task in self.tasks:
            task.join()


def task(depends_on: list[Resource]):
    """Manage launch order and threading for tasks.

    Task wrapped in this must have `Syncher` as a first argument and required resources from
    `depends_on` as next few arguments
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper():
            task_name = func.__name__
            sync = Syncer.get_instance()
            resources = []
            for key in depends_on:
                resources.append(sync.get_resource(key))

            if sync.aborted:
                log(f"Task {task_name} was skipped")
                return None

            try:
                log(f"Starting task {task_name}")
                result = func(sync, *resources)
                log(f"Finished task {task_name}")
                return result
            except BaseException as e:
                log(f"Error in task {task_name}: {e}")
                sync.abort()
                return None

        return wrapper

    return decorator
