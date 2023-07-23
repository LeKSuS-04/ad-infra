from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Config, VulnboxConfig
from tools import Resource, Syncer, task
from tools.paths import (
    ANSIBLE_CONFIG_PATH,
    ANSIBLE_INVENTORY_PATH,
    CONTAINER_REGISTRY_SERVICE_DIR,
    DOCKER_DAEMON_CONFIG_PATH,
    FORCAD_CONFIG_PATH,
    PRIV_SSH_KEY_FILE_PATH,
    PRIVATE_VPN_DIR,
    VPN_JURY_CLIENT_PATH,
    checkers_dir,
    services_dir,
)

from .utils import to_ansible_vunlbox_config

_TEMPLATE_PATH = Path(__file__).parent
_JINJA_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_PATH), autoescape=cast(bool, select_autoescape())
)


def prepare_inventory(
    config: Config,
    vpn_host: str,
    bastion_host: str,
    jury_host: str,
    container_registry_host: str,
    vulnbox_configs: dict[str, VulnboxConfig],
):
    template_params = dict(
        admin_username="admin",
        admin_ssh_key_file_path=PRIV_SSH_KEY_FILE_PATH,
        #
        team_count=len(config.teams),
        network_open_time=config.game.start_time,
        timezone=config.game.timezone,
        vpn_server_files=PRIVATE_VPN_DIR,
        vpn_host=vpn_host,
        #
        bastion_host=bastion_host,
        #
        jury_host=jury_host,
        checkers_path=checkers_dir(config.src_dirname),
        forcad_config_file=FORCAD_CONFIG_PATH,
        jury_vpn_client=VPN_JURY_CLIENT_PATH,
        #
        container_registry_host=container_registry_host,
        docker_daemon_config_file=DOCKER_DAEMON_CONFIG_PATH,
        service_registry_local_path=CONTAINER_REGISTRY_SERVICE_DIR,
        #
        services_path=services_dir(config.src_dirname),
        vulnbox_hosts=to_ansible_vunlbox_config(vulnbox_configs),
    )

    with open(ANSIBLE_INVENTORY_PATH, "w") as f:
        inventory_template = _JINJA_ENV.get_template("inventory.yaml.j2")
        rendered = inventory_template.render(**template_params)
        f.write(cast(str, rendered))


def prepare_config(amount_of_teams: int):
    template_params = dict(forks=amount_of_teams)

    with open(ANSIBLE_CONFIG_PATH, "w") as f:
        inventory_template = _JINJA_ENV.get_template("ansible.cfg.j2")
        rendered = inventory_template.render(**template_params)
        f.write(cast(str, rendered))


@task(
    depends_on=[
        Resource.CONFIG,
        Resource.VULNBOX_CONFIGS,
        Resource.BASTION_HOST_PUBLIC_IP,
        Resource.JURY_HOST_PUBLIC_IP,
        Resource.VPN_HOST_PUBLIC_IP,
        Resource.CONTAINER_REGISTRY_HOST_PUBLIC_IP,
    ],
    depends_on_boolean=[
        Resource.ADMIN_SSH_KEY_FILE_SAVED_TO_DISK,
    ],
    creates=[
        Resource.ANSIBLE_CONFIGURED,
    ],
)
def prepare_ansible(
    sync: Syncer,
    config: Config,
    vulnbox_configs: dict[str, VulnboxConfig],
    bastion_host: str,
    jury_host: str,
    vpn_host: str,
    container_registry_host: str,
):
    prepare_inventory(
        config, vpn_host, bastion_host, jury_host, container_registry_host, vulnbox_configs
    )
    prepare_config(len(config.teams))
    sync.set_resource(Resource.ANSIBLE_CONFIGURED)
