from constants.paths import ANSIBLE_PATH
from tools import Resource, Syncer, task

from .environment import run_with_ansible_env


def run_playbook(playbook_name: str) -> bytes:
    playbook_path = ANSIBLE_PATH / "playbooks" / playbook_name
    return run_with_ansible_env(f"ansible-playbook '{playbook_path}'")


@task(depends_on_boolean=[Resource.VPN_HOST_UP])
def configure_vpn(sync: Syncer):
    run_playbook("vpn_conf.yaml")
    sync.set_resource(Resource.VPN_HOST_CONFIGURED)


@task(depends_on_boolean=[Resource.JURY_HOST_UP])
def configure_jury(sync: Syncer):
    run_playbook("jury_conf.yaml")
    sync.set_resource(Resource.JURY_HOST_CONFIGURED)


@task(depends_on_boolean=[Resource.ALL_VULNBOX_HOSTS_UP])
def configure_vulnboxes(sync: Syncer):
    run_playbook("vulnboxes_conf.yaml")
    sync.set_resource(Resource.ALL_VULNBOX_HOSTS_CONFIGURED)
