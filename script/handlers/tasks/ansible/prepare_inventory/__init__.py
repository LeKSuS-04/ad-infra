from pathlib import Path
from typing import cast
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models import Config
from utils.sync.resources import Resource
from utils.sync import task, Synchronizator
from constants.paths import ANSIBLE_PATH, GENERATED_PATH


TEMPLATE_PATH = Path(__file__).parent
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH), autoescape=cast(bool, select_autoescape())
)


@task(
    depends_on=[
        Resource.ADMIN_SSH_KEY_FILE,
        Resource.BASTION_HOST,
        Resource.JURY_HOST,
        Resource.VPN_HOST,
        Resource.VULNBOX_HOSTS,
    ]
)
def prepare_inventory(
    sync: Synchronizator,
    admin_ssh_key_file: str,
    bastion_host: str,
    jury_host: str,
    vpn_host: str,
    vulnbox_hosts: list[str],
):
    inventory_path = ANSIBLE_PATH / 'inventory.yaml'
    with open(inventory_path, 'w') as f:
        inventory_template = JINJA_ENV.get_template('inventory.yaml.j2')
        rendered = inventory_template.render(
            admin_username='admin',
            admin_ssh_key_file_path=GENERATED_PATH / admin_ssh_key_file,
            bastion_host=bastion_host,
            jury_host=jury_host,
            vpn_host=vpn_host,
            vulnbox_hosts=vulnbox_hosts,
        )
        f.write(cast(str, rendered))
    sync.set_resource(Resource.ANSIBLE_INVENTORY_READY)