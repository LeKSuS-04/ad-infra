import json
from dataclasses import dataclass

from config import Config
from util import REPOSITORY_ROOT, run_process


@dataclass
class ProtectedAddresses:
    jury: str
    monitoring: str


@dataclass
class OnlyRawAddress:
    raw: str


@dataclass
class RawAndDnsAddress:
    raw: str
    dns: str


@dataclass
class OpenAddresses:
    vpn: RawAndDnsAddress
    bastion: RawAndDnsAddress
    jury: OnlyRawAddress
    container_registry: RawAndDnsAddress
    monitoring: OnlyRawAddress


@dataclass
class Vulnbox:
    ip: str


@dataclass
class InternalAddresses:
    # Team number -> Vulnbox
    vulnboxes: dict[int, Vulnbox]


@dataclass
class Addresses:
    # Protected by cloudflare
    protected: ProtectedAddresses
    # Open to the internet
    open: OpenAddresses
    # Internal, accessible only from within the cloud subnet
    internal: InternalAddresses


@dataclass
class TerraformOutput:
    addresses: Addresses


class TerraformController:
    PARALLELISM = 10

    def __init__(self):
        self.terraform_dir = REPOSITORY_ROOT / "terraform"
        self.terraform_config_path = self.terraform_dir / "variables.auto.tfvars.json"

    def apply(self):
        run_process(
            ["terraform", "apply", "-auto-approve", f"-parallelism={self.PARALLELISM}"],
            cwd=self.terraform_dir,
        )

    def output(self) -> TerraformOutput:
        result = run_process(
            ["terraform", "output", "-json"],
            cwd=self.terraform_dir,
        )
        output_dict = json.loads(result.stdout)
        addresses = output_dict["addresses"]["value"]
        return TerraformOutput(
            addresses=Addresses(
                protected=ProtectedAddresses(**addresses["protected"]),
                open=OpenAddresses(
                    vpn=RawAndDnsAddress(**addresses["open"]["vpn"]),
                    bastion=RawAndDnsAddress(**addresses["open"]["bastion"]),
                    jury=OnlyRawAddress(**addresses["open"]["jury"]),
                    container_registry=RawAndDnsAddress(**addresses["open"]["container_registry"]),
                    monitoring=OnlyRawAddress(**addresses["open"]["monitoring"]),
                ),
                internal=InternalAddresses(
                    vulnboxes={
                        int(v["number"]): Vulnbox(ip=v["ip"])
                        for v in addresses["internal"]["vulnboxes"]
                    }
                ),
            )
        )

    def destroy(self):
        run_process(
            ["terraform", "destroy", "-auto-approve", f"-parallelism={self.PARALLELISM}"],
            cwd=self.terraform_dir,
        )

    def save_config(self, config: Config, wireguard_ports: list[int]):
        terraform_config = {
            "yandex_cloud": {
                "folder_id": config.infra.yandex_cloud.folder_id,
                "zone": config.infra.yandex_cloud.zone,
            },
            "cloudflare": {
                "zone_id": config.infra.cloudflare.zone_id,
            },
            "admin_user": {
                "username": config.infra.ssh.username,
                "ssh_keys": config.infra.ssh.public_keys,
            },
            "vulnbox_numbers": [i for i, t in enumerate(config.teams.teams) if t.needs_vulnbox],
            "jury_vm": config.infra.resources.jury.model_dump(mode="json"),
            "vpn_vm": config.infra.resources.vpn.model_dump(mode="json")
            | {
                "wireguard_ports": wireguard_ports,
            },
            "bastion_vm": config.infra.resources.bastion.model_dump(mode="json"),
            "container_registry_vm": config.infra.resources.container_registry.model_dump(
                mode="json"
            ),
            "monitoring_vm": config.infra.resources.monitoring.model_dump(mode="json"),
            "vulnbox_vm": config.infra.resources.vulnbox.model_dump(mode="json"),
        }

        with open(self.terraform_config_path, "w") as f:
            json.dump(terraform_config, f, indent=2)
