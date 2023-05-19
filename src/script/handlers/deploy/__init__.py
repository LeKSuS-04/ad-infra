from handlers.tasks import (
    pack_sources,
    generate_ssh_keys,
    load_config,
    deploy_infrastructure, 
)
from utils.sync.task_manager import TaskManager


def deploy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            pack_sources,
            generate_ssh_keys,
            load_config,
            deploy_infrastructure,
        ]
    )
    task_manager.wait_until_all_finished()
