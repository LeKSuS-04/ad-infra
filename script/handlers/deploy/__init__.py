from tasks import (
    ansible,
    get_ssh_keys,
    load_config,
    terraform,
    vpn,
)
from tools import TaskManager


def deploy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            load_config,
            get_ssh_keys,
            vpn.create_configs,
            terraform.save_terraform_config,
            terraform.deploy_infrastructure,
            ansible.prepare_inventory,
            ansible.ping_all_hosts,
        ]
    )
    task_manager.wait_until_all_finished()
