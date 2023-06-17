from models import Config
from tools import Resource, Syncer, log, task


def total_vms(config: Config) -> int:
    # Vulnbox for each team + jury + bastion + vpn
    return config.terraform_config.vulnbox_count + 3


def total_cores(config: Config) -> int:
    return (
        config.terraform_config.jury_vm.cores
        + config.terraform_config.vpn_vm.cores
        + config.terraform_config.bastion_vm.cores
        + config.terraform_config.vulnbox_vm.cores * config.terraform_config.vulnbox_count
    )


def total_ram(config: Config) -> int:
    return (
        config.terraform_config.jury_vm.ram_gb
        + config.terraform_config.vpn_vm.ram_gb
        + config.terraform_config.bastion_vm.ram_gb
        + config.terraform_config.vulnbox_vm.ram_gb * config.terraform_config.vulnbox_count
    )


def total_ssd(config: Config) -> int:
    return (
        config.terraform_config.jury_vm.ssd_gb
        + config.terraform_config.vpn_vm.ssd_gb
        + config.terraform_config.bastion_vm.ssd_gb
        + config.terraform_config.vulnbox_vm.ssd_gb * config.terraform_config.vulnbox_count
    )


@task(depends_on=[Resource.CONFIG])
def plan_resources(sync: Syncer, config: Config):
    log(
        f"Required resources:\n"
        f"    Virtual machines: {total_vms(config)}\n"
        f"    Cores total: {total_cores(config)}\n"
        f"    RAM GB total: {total_ram(config)}\n"
        f"    SSD GB total: {total_ssd(config)}\n"
    )
