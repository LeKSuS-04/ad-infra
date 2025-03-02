import json
import os
import random
import re
import string
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from config import Config
from controllers.terraform import TerraformOutput
from controllers.wireguard import VpnInfo
from util.log import get_logger
from util.paths import REPOSITORY_ROOT
from util.process import ExecutionResult, run_process


@dataclass
class VulnboxInfo:
    internal_address: str
    team_username: str
    team_password: str
    vpn_client_file: Path


@dataclass
class Inventory:
    admin_user: str
    admin_ssh_key_path: Path

    bastion_address: str
    vpn_address: str
    jury_address: str
    container_registry_address: str
    monitoring_address: str

    vulnbox_info: list[VulnboxInfo]


def _get_active_hosts_from_output(ansible_output: str) -> set[str]:
    hosts = re.findall(r"^([0-9a-z\-\.]+) \| SUCCESS", ansible_output, re.MULTILINE)
    return set(hosts)


class AnsibleController:
    def __init__(self):
        self.ansible_dir = REPOSITORY_ROOT / "ansible"
        self.inventory_path = self.ansible_dir / "inventory.yaml"
        self.ansible_cfg_path = self.ansible_dir / "ansible.cfg"

        self.retries_path = Path(tempfile.gettempdir()) / "ad-infra-ansible-retries"
        self.retries_path.mkdir(exist_ok=True, parents=True)

        self._logger = get_logger("ansible-controller")

    def run_playbook(
        self,
        playbook: Path,
        variables: dict[str, Any] | None = None,
        max_retries: int = 1,
    ) -> ExecutionResult:
        args = ["ansible-playbook", str(playbook), "-i", str(self.inventory_path)]
        if variables:
            json_args = json.dumps(variables)
            args.extend(["--extra-vars", json_args])

        has_succeeded = False
        retries = 0
        exception = None
        while not has_succeeded and retries < max_retries:
            try:
                self._logger.info(f"Running playbook {playbook}")
                result = self._run_ansible_command(args)
                has_succeeded = True
            except Exception as e:
                retries += 1
                self._logger.warning(f"Playbook {playbook} failed: {e}")

                if "--limit" not in args:
                    playbook_name = playbook.stem
                    retry_file = self.retries_path / f"{playbook_name}.retry"
                    if not retry_file.exists():
                        raise ValueError(f"Retry file {retry_file} does not exist")
                    args.extend(["--limit", f"@{retry_file}"])

                exception = e

        if not has_succeeded and exception:
            self._logger.error(f"Playbook {playbook} failed after {retries} retries")
            raise exception

        return result

    def ping(self, inventory: Inventory) -> bool:
        result = self._run_ansible_command(["ansible", "all", "-m", "ping"], check=False)

        active_hosts = _get_active_hosts_from_output(result.stdout)

        all_up = True
        all_hosts = {
            "jury": inventory.jury_address,
            "vpn": inventory.vpn_address,
            "container_registry": inventory.container_registry_address,
            "monitoring": inventory.monitoring_address,
            "bastion": inventory.bastion_address,
        }
        for host, address in all_hosts.items():
            if address not in active_hosts:
                self._logger.info(f"{host} is down :(")
                all_up = False
            else:
                self._logger.info(f"{host} is up!")

        vulnboxes_down = 0
        vulnboxes_up = 0
        for vulnbox in inventory.vulnbox_info:
            if vulnbox.internal_address not in active_hosts:
                self._logger.debug(f"{vulnbox.internal_address} is down :(")
                vulnboxes_down += 1
                all_up = False
            else:
                self._logger.debug(f"{vulnbox.internal_address} is up!")
                vulnboxes_up += 1

        self._logger.info(f"Vulnboxes: {vulnboxes_up} up, {vulnboxes_down} down")

        return all_up

    def create_or_restore_inventory(
        self,
        config: Config,
        vpn_info: VpnInfo,
        tf_output: TerraformOutput,
    ) -> Inventory:
        def create_inventory():
            vulnbox_infos = []
            for vulnbox in tf_output.addresses.internal.vulnboxes:
                vulnbox_vpn = vpn_info.team_configs[vulnbox.number]
                self._logger.info(f"Vulnbox {vulnbox.number} has ip {vulnbox.ip}")
                vulnbox_infos.append(
                    VulnboxInfo(
                        internal_address=vulnbox.ip,
                        team_username=f"team{vulnbox.number:03}",
                        team_password="".join(
                            random.choices(string.ascii_letters + string.digits, k=32)
                        ),
                        vpn_client_file=vulnbox_vpn.base_path / vulnbox_vpn.vulnbox_filename,
                    )
                )

            inventory = Inventory(
                admin_user=config.infra.ssh.username,
                admin_ssh_key_path=config.infra.ssh.private_key_path,
                bastion_address=tf_output.addresses.open.bastion,
                vpn_address=tf_output.addresses.open.vpn,
                container_registry_address=tf_output.addresses.open.container_registry,
                monitoring_address=tf_output.addresses.open.monitoring,
                jury_address=tf_output.addresses.open.jury,
                vulnbox_info=vulnbox_infos,
            )
            return inventory

        if not self.inventory_path.exists():
            return create_inventory()

        inventory_dict = yaml.safe_load(self.inventory_path.read_text())
        vulnbox_hosts = inventory_dict["all"]["children"]["virtualmachines"]["children"]["hosts"]
        vulnbox_infos = []
        for host, info in vulnbox_hosts.items():
            vars = info["vars"]
            vulnbox_infos.append(
                VulnboxInfo(
                    internal_address=host,
                    team_username=vars["username"],
                    team_password=vars["password"],
                    vpn_client_file=vars["vpn_client_file"],
                )
            )

        inventory_addresses = set(host for host in vulnbox_hosts.keys())
        tf_addresses = set(vulnbox.ip for vulnbox in tf_output.addresses.internal.vulnboxes)

        if inventory_addresses != tf_addresses:
            return create_inventory()

        return Inventory(
            admin_user=config.infra.ssh.username,
            admin_ssh_key_path=config.infra.ssh.private_key_path,
            bastion_address=tf_output.addresses.open.bastion,
            vpn_address=tf_output.addresses.open.vpn,
            container_registry_address=tf_output.addresses.open.container_registry,
            monitoring_address=tf_output.addresses.open.monitoring,
            jury_address=tf_output.addresses.open.jury,
            vulnbox_info=vulnbox_infos,
        )

    def save_inventory(self, inventory: Inventory):
        proxy_command = (
            "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p -q"
            f" {inventory.admin_user}@{inventory.bastion_address}"
        )
        host_info = {
            "vulnboxes": {
                "vars": {
                    "ansible_ssh_common_args": f'-o ProxyCommand="{proxy_command}"',
                },
                "hosts": {
                    v.internal_address: {
                        "vars": {
                            "username": v.team_username,
                            "password": v.team_password,
                            "vpn_client_file": str(v.vpn_client_file),
                        },
                    }
                    for v in inventory.vulnbox_info
                },
            },
            "vpn": {
                "hosts": {
                    inventory.vpn_address: {},
                },
            },
            "bastion": {
                "hosts": {
                    inventory.bastion_address: {},
                },
            },
            "jury": {
                "hosts": {
                    inventory.jury_address: {},
                },
            },
            "container_registry": {
                "hosts": {
                    inventory.container_registry_address: {},
                },
            },
            "monitoring": {
                "hosts": {
                    inventory.monitoring_address: {},
                },
            },
        }

        inventory_dict = {
            "all": {
                "children": {
                    "virtualmachines": {
                        "vars": {
                            "ansible_user": inventory.admin_user,
                            "ansible_ssh_private_key_file": str(inventory.admin_ssh_key_path),
                        },
                        "children": host_info,
                    }
                }
            }
        }

        self.inventory_path.write_text(yaml.dump(inventory_dict))
        self._logger.info(f"Inventory saved to {self.inventory_path}")

    def _run_ansible_command(self, command: list[str], check: bool = True) -> ExecutionResult:
        env = os.environ.copy()
        env["ANSIBLE_CONFIG"] = str(self.ansible_cfg_path)
        env["ANSIBLE_INVENTORY"] = str(self.inventory_path)
        env["ANSIBLE_RETRY_FILES_ENABLED"] = "True"
        env["ANSIBLE_RETRY_FILES_SAVE_PATH"] = str(self.retries_path)
        return run_process(command, cwd=self.ansible_dir, env=env, shell=False, check=check)
