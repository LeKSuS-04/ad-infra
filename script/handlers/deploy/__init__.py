from tasks import (
    pack_sources,
    get_ssh_keys,
    load_config,
    vpn,
    terraform,
    ansible,
)
from tools import TaskManager


def deploy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            pack_sources,
            get_ssh_keys,
            load_config,
            vpn.create_configs,
            terraform.deploy_infrastructure,
            ansible.prepare_inventory,
        ]
    )
    task_manager.wait_until_all_finished()
