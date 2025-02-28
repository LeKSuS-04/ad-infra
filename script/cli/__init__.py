import datetime
import json
import random
import string
import time
from pathlib import Path

import click
from config import load_config
from controllers.ansible import AnsibleController, Inventory, VulnboxInfo
from controllers.terraform import TerraformController
from controllers.wireguard import WireguardController
from util.log import get_logger
from util.paths import REPOSITORY_ROOT

logger = get_logger("cli")


@click.group()
def cli():
    pass


@cli.command("deploy")
@click.option(
    "--infra",
    type=click.Path(exists=True),
    required=True,
    help="Path to infra config",
)
@click.option(
    "--teams",
    type=click.Path(exists=True),
    required=True,
    help="Path to teams config",
)
@click.option(
    "--from-scratch",
    is_flag=True,
    help="Destroy existing infrastructure before deploying",
)
def deploy(infra: Path, teams: Path, from_scratch: bool):
    config = load_config(infra, teams)

    terraform = TerraformController()
    if from_scratch:
        logger.info("Destroying existing infrastructure before deploying")
        terraform.destroy()

    vulnbox_port = 30000
    team_port = 31000

    logger.info("Deploying infrastructure")
    terraform.save_config(config, [vulnbox_port, team_port])
    terraform.apply()
    tf_output = terraform.output()
    logger.info(f"Got Terraform output: {tf_output}")

    wireguard = WireguardController(
        server_address=tf_output.addresses.open.vpn,
        vulnbox_port=vulnbox_port,
        team_port=team_port,
    )

    team_count = len(tf_output.addresses.internal.vulnboxes)
    generated = REPOSITORY_ROOT / "generated"
    paths = wireguard.generate_configs(
        total_teams=team_count,
        per_team=config.infra.teams.players_per_team,
        server_output_dir=generated / "server",
        team_output_dir=generated / "teams",
        get_team_dir_name=lambda x: f"team{x:03}",
    )

    vulnbox_infos = []
    for i, team_paths in enumerate(paths.team_configs):
        vulnbox_infos.append(
            VulnboxInfo(
                internal_address=tf_output.addresses.internal.vulnboxes[i],
                team_username=f"team{i:03}",
                team_password="".join(random.choices(string.ascii_letters + string.digits, k=32)),
                vpn_client_file=team_paths.base_path / team_paths.vulnbox_filename,
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

    ansible = AnsibleController()
    ansible.save_inventory(inventory)

    all_hosts_up = ansible.ping(inventory)
    while not all_hosts_up:
        logger.info("Some hosts are still down. Waiting for all hosts to be up...")
        time.sleep(5)
        all_hosts_up = ansible.ping(inventory)

    playbooks_path = REPOSITORY_ROOT / "ansible" / "playbooks"
    # ansible.run_playbook(
    #     playbooks_path / "vpn_conf.yaml",
    #     variables={
    #         "vpn_server_files": [str(path) for path in paths.server_configs],
    #         "team_count": len(config.teams.teams),
    #         "timezone": config.infra.forcad.game.timezone,
    #         "network_open_time": config.infra.forcad.game.start_time.strftime("%Y%m%d%H%M.%S"),
    #     },
    #     max_retries=3,
    # )

    docker_daemon_config_file = generated / "daemon.json"
    daemon_config = {
        "registry-mirrors": [
            f"https://{tf_output.addresses.open.container_registry}",
        ],
    }
    docker_daemon_config_file.write_text(json.dumps(daemon_config, indent=2))

    ansible.run_playbook(
        playbooks_path / "jury_conf.yaml",
        variables={
            "team_count": len(config.teams.teams),
            "timezone": config.infra.forcad.game.timezone,
            "network_open_time": config.infra.forcad.game.start_time.strftime("%Y%m%d%H%M.%S"),
            "docker_daemon_config_file": str(docker_daemon_config_file),
        },
        max_retries=3,
    )

    services_path = REPOSITORY_ROOT / "services"
    ansible.run_playbook(
        playbooks_path / "registry_conf.yaml",
        variables={
            "domain": tf_output.addresses.open.container_registry,
            "docker_daemon_config_file": str(docker_daemon_config_file),
            "service_registry_local_path": str(services_path / "container_registry"),
        },
        max_retries=3,
    )


@cli.command("destroy")
def destroy():
    terraform = TerraformController()
    terraform.destroy()
