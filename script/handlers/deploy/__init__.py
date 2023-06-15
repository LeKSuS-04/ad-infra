from tasks import (
    ansible,
    generate_vulnbox_configs,
    get_ssh_keys,
    load_config,
    save_forcad_config,
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
            generate_vulnbox_configs,
            save_forcad_config,
            ansible.prepare_inventory,
            ansible.ping_all_hosts,
            ansible.configure_vpn,
            ansible.configure_jury,
            ansible.configure_vulnboxes,
        ]
    )
    task_manager.wait_until_all_finished()
