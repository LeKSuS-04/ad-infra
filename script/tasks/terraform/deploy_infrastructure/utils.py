import re
from pathlib import Path
from typing import cast, Callable, Any
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives import serialization
from jinja2 import Environment, FileSystemLoader, select_autoescape

from constants.paths import TERRAFORM_PATH
from tools import Syncer, Resource, log


TEMPLATE_PATH = Path(__file__).parent
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH),
    autoescape=cast(bool, select_autoescape()),
)


class _TerraformOutputParser:
    def __init__(
        self,
        resource: Resource,
        terraform_variable: str,
        processer: Callable[[str], Any],
    ):
        self.resource = resource
        self.terraform_variable = terraform_variable
        self.processer = processer

    def get_terraform_output_variable(self, terraform_output: str) -> str:
        variable_match = re.search(
            self.terraform_variable + r' = "(?P<value>.*)"', terraform_output
        )
        if variable_match is None:
            raise ValueError(
                f'Terraform output does not contain value for variable "{self.terraform_variable}"'
            )
        return variable_match.group("value")

    def process(self, sync: Syncer, terraform_output: str):
        value = self.get_terraform_output_variable(terraform_output)
        sync.set_resource(self.resource, self.processer(value))


def save_cloud_init_config(ssh_key: EllipticCurvePrivateKey):
    cloud_init_config_path = TERRAFORM_PATH / "cloud-init.yaml"
    with open(cloud_init_config_path, "w") as f:
        cloud_init_template = JINJA_ENV.get_template("cloud-init.yaml.j2")
        public_key = (
            ssh_key.public_key()
            .public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
            .decode()
        )
        rendered = cloud_init_template.render(public_key=public_key)
        f.write(cast(str, rendered))
        log(f"Saved cloud-init config into {cloud_init_config_path}")


def save_resources(sync: Syncer, terraform_output: str):
    identity = lambda x: x  # noqa: E731
    parsers = [
        _TerraformOutputParser(
            resource=Resource.VPN_HOST,
            terraform_variable="vpn_address",
            processer=identity,
        ),
        _TerraformOutputParser(
            resource=Resource.JURY_HOST,
            terraform_variable="jury_address",
            processer=identity,
        ),
        _TerraformOutputParser(
            resource=Resource.BASTION_HOST,
            terraform_variable="bastion_address",
            processer=identity,
        ),
        _TerraformOutputParser(
            resource=Resource.VULNBOX_HOSTS,
            terraform_variable="vulnbox_internal_addresses",
            processer=lambda x: x.split(" "),
        ),
    ]
    for parser in parsers:
        parser.process(sync, terraform_output)
