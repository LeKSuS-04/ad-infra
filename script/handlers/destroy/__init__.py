from tasks import (
    clean_filesystem,
    terraform,
)
from tools import TaskManager


def destroy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            terraform.destroy_infrastructure,
            clean_filesystem,
        ]
    )
    task_manager.run_tasks()
