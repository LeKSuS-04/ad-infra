from tasks import other, terraform
from tools import TaskManager


def destroy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            terraform.destroy_infrastructure,
            other.clean_filesystem,
        ]
    )
    task_manager.run_tasks()
