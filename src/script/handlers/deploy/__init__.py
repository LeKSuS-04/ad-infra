from handlers.tasks.load_config import load_config
from handlers.tasks.deploy_infrastructure import deploy_infrastructure
from handlers.tasks.generate_ssh_keys import generate_ssh_keys
from handlers.tasks.task_manager import TaskManager


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
