import re
from collections.abc import Callable
from typing import Any

from tools import Resource, Syncer


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


def save_resources(sync: Syncer, terraform_output: str):
    identity = lambda x: x  # noqa: E731
    parsers = [
        _TerraformOutputParser(
            resource=Resource.VPN_HOST_IP,
            terraform_variable="vpn_address",
            processer=identity,
        ),
        _TerraformOutputParser(
            resource=Resource.JURY_HOST_IP,
            terraform_variable="jury_address",
            processer=identity,
        ),
        _TerraformOutputParser(
            resource=Resource.BASTION_HOST_IP,
            terraform_variable="bastion_address",
            processer=identity,
        ),
        _TerraformOutputParser(
            resource=Resource.VULNBOX_HOSTS_IPS,
            terraform_variable="vulnbox_internal_addresses",
            processer=lambda x: x.split(" "),
        ),
    ]
    for parser in parsers:
        parser.process(sync, terraform_output)
