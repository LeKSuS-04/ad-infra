import threading
from typing import Any

from tools.singleton import Singleton

from .resources import Resource


class _Storage:
    def __init__(self):
        self._resources = {key: None for key in Resource}
        self._storage_lock = threading.Lock()

    def __setitem__(self, key: Resource, value: Any) -> Any:
        with self._storage_lock:
            self._resources[key] = value
            return value

    def __getitem__(self, key: Resource) -> Any:
        with self._storage_lock:
            return self._resources[key]


class Syncer(metaclass=Singleton):
    def __init__(self):
        self._events = {key: threading.Event() for key in Resource}
        self._storage = _Storage()
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
            raise ValueError(f"Resource {key} is being set second time")

        self._storage[key] = value
        self._events[key].set()
        return self._storage[key]

    def get_resource(self, key: Resource) -> Any:
        self.wait_for(key)
        return self._storage[key]

    @classmethod
    def get_instance(cls):
        return Syncer()
