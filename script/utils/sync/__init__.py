import threading
from typing import Any, Callable
from functools import wraps

from .resources import Resource
from .storage import Storage
from utils.logger import log
from utils.singleton import Singleton


class Synchronizator(metaclass=Singleton):
    def __init__(self):
        self._events = {key: threading.Event() for key in Resource}
        self._storage = Storage()
        self.aborted = False

    def abort(self):
        self.aborted = True
        for key in self._events.keys():
            self._events[key].set()

    def wait_for(self, key: Resource):
        self._events[key].wait()

    def set_resource(self, key: Resource, value: Any = True) -> Any:
        if self.aborted:
            return

        if self._events[key].is_set():
            raise ValueError(f'Resource {key} is being set second time')

        self._storage[key] = value
        self._events[key].set()
        return self._storage[key]

    def get_resource(self, key: Resource) -> Any:
        self.wait_for(key)
        return self._storage[key]

    @classmethod
    def get_instance(cls):
        return Synchronizator()


def task(depends_on: list[Resource]):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper():
            task_name = func.__name__
            sync = Synchronizator.get_instance()
            resources = []
            for key in depends_on:
                resources.append(sync.get_resource(key))

            if sync.aborted:
                log(f'Task {task_name} was skipped')
                return None

            try:
                log(f'Starting task {task_name}')
                result = func(sync, *resources)
                log(f'Finished task {task_name}')
                return result
            except BaseException as e:
                log(f'Error in task {task_name}: {e}')
                sync.abort()
                return None

        return wrapper

    return decorator
