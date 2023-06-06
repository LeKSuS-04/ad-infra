import threading
from typing import Any

from .resources import Resource


class Storage():
    def __init__(self):
        self._resources = {
            key: None for key in Resource
        }
        self._storage_lock = threading.Lock()
    
    def __setitem__(self, key: Resource, value: Any) -> Any:
        with self._storage_lock:
            self._resources[key] = value
            return value

    def __getitem__(self, key: Resource) -> Any:
        with self._storage_lock:
            return self._resources[key]