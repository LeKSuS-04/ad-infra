from tasks import (
    ansible,
    pack_team_archives,
)
from tools import TaskManager


def deploy():
    task_manager = TaskManager()
    task_manager.add_tasks(
        [
            ansible.configure_vpn,
            ansible.configure_jury,
            ansible.configure_vulnboxes,
            pack_team_archives,
        ]
    )
    task_manager.run_tasks()
