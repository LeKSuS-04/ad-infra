from handlers.tasks import (
    pack_sources,
    generate_ssh_keys,
    load_config,
    ovpngen_create_configs,
    terraform,
    ansible,
)
from utils.sync.task_manager import TaskManager


def deploy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            pack_sources,
            generate_ssh_keys,
            load_config,
            # ovpngen_create_configs,
            terraform.deploy_infrastructure,
            ansible.prepare_inventory,
        ]
    )
    task_manager.wait_until_all_finished()
