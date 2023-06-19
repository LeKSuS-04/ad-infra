import threading
from collections import defaultdict
from enum import Enum, auto
from queue import Queue

from tools.syncer.resources import Resource

from .task import Task


class _CycleFoundError(AssertionError):
    def __init__(self, resource_cycle: list[Resource], resources_to_task: dict[Resource, Task]):
        message = f"Found cycle in resource dependencies: {resource_cycle[0]}"
        producers_names = []
        longest_name = ""
        for resource in resource_cycle[1:]:
            producer_name = resources_to_task[resource].name
            producers_names.append(producer_name)
            if len(producer_name) > len(longest_name):
                longest_name = producer_name

        for resource in resource_cycle[1:]:
            producer = resources_to_task[resource]
            formatted_name = f'"{producer.name}"' + " " * (len(longest_name) - len(producer.name))
            message += f"\n that depends on {formatted_name} (because of {resource})"
        super(__class__, self).__init__(message)


def _create_resource_to_task_mapping() -> dict[Resource, Task]:
    from tasks import TASK_LIST

    resources_to_tasks: dict[Resource, Task] = dict()

    for task in TASK_LIST:
        for resource in task.creates:
            if resource in resources_to_tasks.keys():
                raise ValueError(
                    f"Resource {resource} is in multiple tasks: "
                    f"{resources_to_tasks[resource].name} and {task.name}"
                )
            resources_to_tasks[resource] = task
    for resource in Resource:
        if resource not in resources_to_tasks.keys():
            raise ValueError(f"No task produces resource {resource}")

    return resources_to_tasks


class TaskManager:
    def __init__(self):
        self._tasks: set[Task] = set()
        self._resources_to_tasks: dict[Resource, Task] = _create_resource_to_task_mapping()

    def add_tasks(self, new_tasks: list[Task]):
        for task in new_tasks:
            self._tasks.add(task)

    def _add_dependencies(self):
        class Status(Enum):
            UNKNOWN = auto()
            HANDLED = auto()

        resource_status: defaultdict[Resource, Status] = defaultdict(lambda: Status.UNKNOWN)
        required_resources = Queue()
        for producer in self._tasks:
            for resource in producer.dependencies:
                required_resources.put(resource)

        while not required_resources.empty():
            resource = required_resources.get(block=False)
            if resource_status[resource] == Status.HANDLED:
                continue

            producer = self._resources_to_tasks[resource]
            self._tasks.add(producer)
            resource_status[resource] = Status.HANDLED

            for dependency in producer.dependencies:
                if resource_status[dependency] != Status.HANDLED:
                    required_resources.put(dependency)

    def _ensure_no_cycles(self):
        class Status(Enum):
            UNKNOWN = auto()
            VISITED = auto()
            EXPLORED = auto()

        resource_status: defaultdict[Resource, Status] = defaultdict(lambda: Status.UNKNOWN)
        resource_parent: dict[Resource, Resource] = dict()

        def dfs(source: Resource):
            resource_status[source] = Status.VISITED

            producer = self._resources_to_tasks[source]
            for dependency in producer.dependencies:
                match resource_status[dependency]:
                    case Status.UNKNOWN:
                        resource_parent[dependency] = source
                        dfs(dependency)

                    case Status.VISITED:
                        cycle = [dependency, source]
                        current = resource_parent[source]
                        while current != dependency:
                            cycle.append(current)
                            current = resource_parent[current]
                        cycle.append(dependency)
                        raise _CycleFoundError(cycle[::-1], self._resources_to_tasks)

                    case Status.EXPLORED:
                        pass

            resource_status[source] = Status.EXPLORED

        for task in self._tasks:
            for resource in task.dependencies:
                if resource_status[resource] == Status.UNKNOWN:
                    dfs(resource)

    def run_tasks(self):
        self._add_dependencies()
        self._ensure_no_cycles()

        threads = []
        for task in self._tasks:
            thread = threading.Thread(target=task, name=task.name)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
