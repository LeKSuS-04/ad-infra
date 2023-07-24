from models import Config
from tools import Resource, Syncer, log, task


def _total_vms(config: Config) -> int:
    # Vulnbox for each team + jury + bastion + vpn + container registry
    return config.terraform_config.vulnbox_count + 4


def _total_cores(config: Config) -> int:
    return (
        config.terraform_config.jury_vm.cores
        + config.terraform_config.vpn_vm.cores
        + config.terraform_config.bastion_vm.cores
        + config.terraform_config.container_registry_vm.cores
        + config.terraform_config.vulnbox_vm.cores * config.terraform_config.vulnbox_count
    )


def _total_ram(config: Config) -> int:
    return (
        config.terraform_config.jury_vm.ram_gb
        + config.terraform_config.vpn_vm.ram_gb
        + config.terraform_config.bastion_vm.ram_gb
        + config.terraform_config.container_registry_vm.ram_gb
        + config.terraform_config.vulnbox_vm.ram_gb * config.terraform_config.vulnbox_count
    )


def _total_ssd(config: Config) -> int:
    return (
        config.terraform_config.jury_vm.ssd_gb
        + config.terraform_config.vpn_vm.ssd_gb
        + config.terraform_config.bastion_vm.ssd_gb
        + config.terraform_config.container_registry_vm.ssd_gb
        + config.terraform_config.vulnbox_vm.ssd_gb * config.terraform_config.vulnbox_count
    )


@task(depends_on=[Resource.CONFIG])
def plan_resources(sync: Syncer, config: Config):
    log(
        f"Required resources:\n"
        f"    Virtual machines: {_total_vms(config)}\n"
        f"    Cores total: {_total_cores(config)}\n"
        f"    RAM GB total: {_total_ram(config)}\n"
        f"    SSD GB total: {_total_ssd(config)}\n"
    )
