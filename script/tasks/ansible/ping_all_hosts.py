import re
from time import sleep

from tools import Resource, Syncer, log, task

from .environment import run_with_ansible_env

_ATTEMPT_INTERVAL_SECONDS = 5


def _get_active_hosts_from_output(ansible_output: str) -> set[str]:
    hosts = re.findall(r"([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}) \| SUCCESS", ansible_output)
    return set(hosts)


def _get_status_str(status_up: bool) -> str:
    return "up" if status_up else "down"


def _get_active_hosts() -> set[str]:
    try:
        output = run_with_ansible_env("ansible all -m ping")
        return _get_active_hosts_from_output(output.decode())
    except ValueError as ex:
        # If 'code 4' in exception, that means that ansilbe process terminated with exit code 4.
        # Ansible terminates with code 4 if some targets are unreachable, which is expected on
        # a couple of first iterations.
        if 'code 4' not in str(ex):
            raise ex
        return set()


@task(
    depends_on=[
        Resource.JURY_HOST_IP,
        Resource.VPN_HOST_IP,
        Resource.VULNBOX_HOSTS_IPS,
    ],
    depends_on_boolean=[
        Resource.ANSIBLE_CONFIGURED,
    ],
    creates=[
        Resource.JURY_HOST_UP,
        Resource.VPN_HOST_UP,
        Resource.ALL_VULNBOX_HOSTS_UP,
    ],
)
def ping_all_hosts(sync: Syncer, jury_host: str, vpn_host: str, vulnbox_hosts: str):
    jury_up = False
    vpn_up = False
    all_vulnboxes_up = False

    while True:
        log("Pinging hosts")
        active_hosts = _get_active_hosts()

        if not jury_up:
            jury_up |= jury_host in active_hosts
            if jury_up:
                sync.set_resource(Resource.JURY_HOST_UP)
                log("Jury is up!")

        if not vpn_up:
            vpn_up |= vpn_host in active_hosts
            if vpn_up:
                sync.set_resource(Resource.VPN_HOST_UP)
                log("VPN is up!")

        vulnbox_active_count = sum(host in active_hosts for host in vulnbox_hosts)
        if not all_vulnboxes_up:
            all_vulnboxes_up |= vulnbox_active_count == len(vulnbox_hosts)
            if all_vulnboxes_up:
                sync.set_resource(Resource.ALL_VULNBOX_HOSTS_UP)
                log("All vulnboxes are up!")

        log(
            f"Host statuses summary: "
            f"jury {_get_status_str(jury_up)}, "
            f"vpn {_get_status_str(vpn_up)}, "
            f"vulnboxes {vulnbox_active_count} up out of {len(vulnbox_hosts)}"
        )

        if jury_up and vpn_up and all_vulnboxes_up:
            log("All hosts are up!")
            return
        else:
            log(f"Some hosts are down, going to retry in {_ATTEMPT_INTERVAL_SECONDS} seconds")
            sleep(_ATTEMPT_INTERVAL_SECONDS)
