from tasks import (
    clean_filesystem,
    get_ssh_keys,
    load_config,
    terraform,
)
from tools import TaskManager


def destroy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            load_config,
            get_ssh_keys,
            terraform.save_terraform_config,
            terraform.destroy_infrastructure,
            clean_filesystem,
        ]
    )
    task_manager.wait_until_all_finished()
