import threading
from typing import Callable

class TaskManager:
    def __init__(self):
        self.tasks: list[threading.Thread] = []

    def add_tasks(self, tasks: list[Callable]):
        for task in tasks:
            process = threading.Thread(target=task)
            process.start()
            self.tasks.append(process)

    def wait_until_all_finished(self):
        for task in self.tasks:
            task.join()
