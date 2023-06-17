from collections.abc import Callable

from tools.logger import log
from tools.syncer import Syncer
from tools.syncer.resources import Resource


class Task:
    """Single task with resource properties.

    Task wrapped in this must have `Syncher` as a first argument and required resources from
    `depends_on` as next few arguments. If resource is required to exist, but is not needed
    as a direct argument, it must be placed into `depends_on_boolean` argument.

    Task wrapped in this must set resources all from `creates` in syncher while executing.
    """

    def __init__(
        self,
        function: Callable,
        depends_on: list[Resource] = [],
        depends_on_boolean: list[Resource] = [],
        creates: list[Resource] = [],
    ):
        self._function = function
        self._depends_on = depends_on
        self._depends_on_boolean = depends_on_boolean
        self._creates = creates

    @property
    def name(self) -> str:
        return self._function.__name__

    @property
    def dependencies(self) -> list[Resource]:
        return self._depends_on + self._depends_on_boolean

    @property
    def creates(self) -> list[Resource]:
        return self._creates

    def __call__(self):
        sync = Syncer.get_instance()
        for key in self._depends_on_boolean:
            sync.wait_for(key)

        resources = []
        for key in self._depends_on:
            resources.append(sync.get_resource(key))

        if sync.aborted:
            log(f"Task {self.name} was skipped")
            return None

        try:
            log(f"Starting task {self.name}")
            result = self._function(sync, *resources)
            log(f"Finished task {self.name}")
            return result
        except BaseException as e:
            log(f"Error in task {self.name}: {e}")
            log("Going to finish running tasks, all others will be skipped")
            sync.abort()
            return None


def task(
    depends_on: list[Resource] = [],
    depends_on_boolean: list[Resource] = [],
    creates: list[Resource] = [],
):
    def decorator(func: Callable):
        return Task(func, depends_on, depends_on_boolean, creates)

    return decorator
