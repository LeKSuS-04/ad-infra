from handlers.tasks import generate_ssh_keys, load_config, deploy_infrastructure
from synchronization.task_manager import TaskManager


def deploy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            generate_ssh_keys,
            load_config,
            deploy_infrastructure,
        ]
    )
    task_manager.wait_until_all_finished()
