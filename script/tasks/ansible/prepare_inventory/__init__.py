from pathlib import Path
from typing import cast

from constants.paths import ANSIBLE_PATH, GENERATED_PATH, INTERNAL_PATH
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Config, VulnboxConfig
from tools import Resource, Syncer, task

TEMPLATE_PATH = Path(__file__).parent
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH), autoescape=cast(bool, select_autoescape())
)


@task(
    depends_on=[
        Resource.CONFIG,
        Resource.ADMIN_SSH_KEY_FILE,
        Resource.VULNBOX_CONFIGS,
        Resource.BASTION_HOST,
        Resource.JURY_HOST,
        Resource.VPN_HOST,
    ]
)
def prepare_inventory(
    sync: Syncer,
    config: Config,
    admin_ssh_key_file: str,
    vulnbox_configs: list[VulnboxConfig],
    bastion_host: str,
    jury_host: str,
    vpn_host: str,
):
    inventory_path = ANSIBLE_PATH / "inventory.yaml"

    template_params = dict(
        admin_username="admin",
        admin_ssh_key_file_path=GENERATED_PATH / admin_ssh_key_file,
        #
        team_count=len(config.teams),
        network_open_time=config.network.open_time,
        timezone=config.network.timezone,
        vpn_host=vpn_host,
        #
        bastion_host=bastion_host,
        #
        jury_host=jury_host,
        jury_vpn_client=INTERNAL_PATH / "vpn" / "jury" / "client" / "config.ovpn",
        #
        vulnbox_hosts={
            host.real_ip: dict(
                vpn_file=host.local_vpn_config_path,
                user=host.username,
                password=host.password,
            )
            for host in vulnbox_configs
        },
    )

    with open(inventory_path, "w") as f:
        inventory_template = JINJA_ENV.get_template("inventory.yaml.j2")
        rendered = inventory_template.render(**template_params)
        f.write(cast(str, rendered))
    sync.set_resource(Resource.ANSIBLE_INVENTORY_READY)
