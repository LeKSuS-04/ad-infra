from pathlib import Path
from typing import cast

from constants.paths import (
    ANSIBLE_INVENTORY_PATH,
    FORCAD_CONFIG_PATH,
    PRIV_SSH_KEY_FILE_PATH,
    VPN_JURY_CLIENT_PATH,
    checkers_dir,
    services_dir,
)
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Config, VulnboxConfig
from tools import Resource, Syncer, task

from .utils import get_all_vpn_server_paths, to_ansible_vunlbox_config

_TEMPLATE_PATH = Path(__file__).parent
_JINJA_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_PATH), autoescape=cast(bool, select_autoescape())
)


@task(
    depends_on=[
        Resource.CONFIG,
        Resource.VULNBOX_CONFIGS,
        Resource.BASTION_HOST,
        Resource.JURY_HOST,
        Resource.VPN_HOST,
    ],
    depends_on_boolean=[
        Resource.ADMIN_SSH_KEY_FILE_SAVED,
    ],
)
def prepare_inventory(
    sync: Syncer,
    config: Config,
    vulnbox_configs: list[VulnboxConfig],
    bastion_host: str,
    jury_host: str,
    vpn_host: str,
):
    template_params = dict(
        admin_username="admin",
        admin_ssh_key_file_path=PRIV_SSH_KEY_FILE_PATH,
        #
        team_count=len(config.teams),
        network_open_time=config.game.start_time,
        timezone=config.game.timezone,
        vpn_server_files=get_all_vpn_server_paths(config),
        vpn_host=vpn_host,
        #
        bastion_host=bastion_host,
        #
        jury_host=jury_host,
        checkers_path=checkers_dir(config.src_dirname),
        forcad_config_file=FORCAD_CONFIG_PATH,
        jury_vpn_client=VPN_JURY_CLIENT_PATH,
        #
        services_path=services_dir(config.src_dirname),
        vulnbox_hosts=to_ansible_vunlbox_config(vulnbox_configs),
    )

    with open(ANSIBLE_INVENTORY_PATH, "w") as f:
        inventory_template = _JINJA_ENV.get_template("inventory.yaml.j2")
        rendered = inventory_template.render(**template_params)
        f.write(cast(str, rendered))
    sync.set_resource(Resource.ANSIBLE_INVENTORY_READY)
