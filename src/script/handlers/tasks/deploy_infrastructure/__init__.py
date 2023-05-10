import re
from pathlib import Path
from typing import cast
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives import serialization
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models import Config
from synchronization import Synchronizator
from synchronization.resources import Resource
from utils.logger import log
from utils.process import process


TEMPLATE_PATH = Path(__file__).parent
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH),
    autoescape=cast(bool, select_autoescape()),
)

TERRAFORM_DIR_PATH = Path.cwd() / 'terraform'


class MachineIpInfo(BaseModel):
    resource: Resource
    terraform_variable: str


def save_terraform_config(sync: Synchronizator):
    config: Config = sync.get_resource(Resource.CONFIG)
    terraform_config_path = TERRAFORM_DIR_PATH / 'variables.auto.tfvars.json'
    with open(terraform_config_path, 'w') as f:
        f.write(config.terraform_config.json())
        log(f'saved terraform configuration into {terraform_config_path}')


def save_cloud_init_config(sync: Synchronizator):
    ssh_key: EllipticCurvePrivateKey = sync.get_resource(Resource.ADMIN_SSH_KEY)
    cloud_init_config_path = TERRAFORM_DIR_PATH / 'cloud-init.yaml'
    with open(cloud_init_config_path, 'w') as f:
        cloud_init_template = JINJA_ENV.get_template('cloud-init.yaml.j2')
        public_key = ssh_key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        ).decode()
        rendered = cloud_init_template.render(public_key=public_key)
        f.write(cast(str, rendered))
        log(f'saved cloud-init config into {cloud_init_config_path}')


def get_terraform_output_variable(terraform_output: str, var_name: str) -> str:
    variable_match = re.search(var_name + r' = "(?P<value>.*)"', terraform_output)
    if variable_match is None:
        raise ValueError(f'terraform output does not contain value for variable "{var_name}"')
    return variable_match.group('value')


def save_resources(terraform_output: str, sync: Synchronizator):
    mapping = [
        MachineIpInfo(resource=Resource.VPN_ADDRESS, terraform_variable='vpn_address'),
        MachineIpInfo(resource=Resource.JURY_ADDRESS, terraform_variable='jury_address'),
        MachineIpInfo(resource=Resource.BASTION_ADDRESS, terraform_variable='bastion_address'),
    ]
    for machine_ip_info in mapping:
        machine_ip = get_terraform_output_variable(
            terraform_output, machine_ip_info.terraform_variable
        )
        sync.set_resource(machine_ip_info.resource, machine_ip)


@Synchronizator.task(depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY])
def deploy_infrastructure(sync: Synchronizator):
    save_terraform_config(sync)
    save_cloud_init_config(sync)

    stdout = process('terraform apply -auto-approve', cwd=TERRAFORM_DIR_PATH)

    terraform_output = stdout.decode()
    save_resources(terraform_output, sync)
