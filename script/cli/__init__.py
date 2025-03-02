import json
import re
import shutil
import time
from pathlib import Path

import click
from config import load_config
from controllers.ansible import AnsibleController
from controllers.forcad import ForcadController
from controllers.team_archive import InstanceInfo, TeamArchiveController, TeamInfo
from controllers.terraform import TerraformController
from controllers.wireguard import WireguardController
from util.exc_thread import ExceptionThread
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
    default="config.yaml",
    help="Path to infra config",
)
@click.option(
    "--teams",
    type=click.Path(exists=True),
    required=True,
    default="teams.yaml",
    help="Path to teams config",
)
@click.option(
    "--from-scratch",
    is_flag=True,
    help="Destroy existing infrastructure before deploying",
)
def deploy(infra: Path, teams: Path, from_scratch: bool):
    if from_scratch:
        logger.info("Destroying existing infrastructure before deploying")
        destroy_impl()

    config = load_config(infra, teams)
    generated = REPOSITORY_ROOT / "generated"

    tf_output, vpn_info = setup_infrastructure(config, generated)

    forcad_config_path, docker_daemon_config_file = configure_services(
        config, vpn_info, tf_output, generated
    )

    team_tokens = deploy_and_configure_hosts(
        config, vpn_info, tf_output, forcad_config_path, docker_daemon_config_file
    )

    create_team_archives(config, vpn_info, tf_output, team_tokens, generated)

    logger.info("All done!")


def setup_infrastructure(config, generated):
    vulnbox_port = 30000
    team_port = 31000
    jury_port = 31789

    logger.info("Deploying infrastructure")
    terraform = TerraformController()
    terraform.save_config(config, [vulnbox_port, team_port, jury_port])
    terraform.apply()
    tf_output = terraform.output()
    logger.info(f"Got Terraform output: {tf_output}")

    wireguard = WireguardController(
        server_address=tf_output.addresses.open.vpn,
        vulnbox_port=vulnbox_port,
        team_port=team_port,
        jury_port=jury_port,
    )

    team_count = len(config.teams.teams)
    vpn_info = wireguard.generate_configs(
        total_teams=team_count,
        per_team=config.infra.teams.players_per_team,
        server_output_dir=generated / "server",
        team_output_dir=generated / "teams",
        jury_output_path=generated / "jury.conf",
        get_team_dir_name=lambda x: f"team{x:03}",
    )

    return tf_output, vpn_info


def configure_services(config, vpn_info, tf_output, generated):
    forcad_config_path = generated / "forcad.yaml"
    forcad_controller = ForcadController()
    forcad_controller.save_forcad_config(config, vpn_info, forcad_config_path)

    registry_address = tf_output.addresses.open.container_registry.replace("registry", "containers")
    docker_daemon_config_file = generated / "docker-daemon.json"
    daemon_config = {
        "registry-mirrors": [
            f"https://{registry_address}",
        ],
    }
    docker_daemon_config_file.write_text(json.dumps(daemon_config, indent=2))

    return forcad_config_path, docker_daemon_config_file


def deploy_and_configure_hosts(
    config, vpn_info, tf_output, forcad_config_path, docker_daemon_config_file
):
    ansible = AnsibleController()
    inventory = ansible.create_or_restore_inventory(config, vpn_info, tf_output)

    all_hosts_up = ansible.ping(inventory)
    while not all_hosts_up:
        logger.info("Some hosts are still down. Waiting for all hosts to be up...")
        time.sleep(5)
        all_hosts_up = ansible.ping(inventory)

    playbooks_path = REPOSITORY_ROOT / "ansible" / "playbooks"

    ansible.run_playbook(
        playbooks_path / "vpn_conf.yaml",
        variables={
            "vpn_server_files": [str(path) for path in vpn_info.server_config_paths],
            "team_count": len(config.teams.teams),
            "timezone": config.infra.forcad.game.timezone,
            "network_open_time": config.infra.forcad.game.start_time.strftime("%Y%m%d%H%M.%S"),
        },
        max_retries=3,
    )

    services_path = REPOSITORY_ROOT / "services"
    ansible.run_playbook(
        playbooks_path / "container_registry_conf.yaml",
        variables={
            "domain": tf_output.addresses.open.container_registry.replace("registry", "containers"),
            "docker_daemon_config_file": str(docker_daemon_config_file),
            "registry_path": str(services_path / "container_registry"),
        },
        max_retries=3,
    )

    configure_jury_and_vulnboxes(
        config, vpn_info, forcad_config_path, docker_daemon_config_file, playbooks_path, ansible
    )

    return run_jury_and_get_tokens(playbooks_path, ansible)


def configure_jury_and_vulnboxes(
    config, vpn_info, forcad_config_path, docker_daemon_config_file, playbooks_path, ansible
):
    def run_configure_jury_playbook():
        ansible.run_playbook(
            playbooks_path / "jury_conf.yaml",
            variables={
                "docker_daemon_config_file": str(docker_daemon_config_file),
                "vpn_client_file": str(vpn_info.jury_config_path),
                "checkers_path": str(config.infra.repository.checkers_path.absolute()),
                "forcad_config_file": str(forcad_config_path),
            },
            max_retries=3,
        )

    def run_configure_vunlboxes_playbook():
        ansible.run_playbook(
            playbooks_path / "vulnboxes_conf.yaml",
            variables={
                "services_path": str(config.infra.repository.services_path.absolute()),
                "docker_daemon_config_file": str(docker_daemon_config_file),
            },
            max_retries=10,
        )

    threads = [
        ExceptionThread(run_configure_jury_playbook, name="configure-jury"),
        ExceptionThread(run_configure_vunlboxes_playbook, name="configure-vulnboxes"),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def run_jury_and_get_tokens(playbooks_path, ansible):
    result = ansible.run_playbook(
        playbooks_path / "jury_run.yaml",
        max_retries=3,
    )
    team_tokens_match = re.search(r'"team_tokens\.stdout": "(?P<tokens>.*)"', result.stdout)
    if team_tokens_match is None:
        raise ValueError("Can't find team tokens in ForcAD output from Ansible")

    teams_to_tokens = team_tokens_match.group("tokens").split("\\n")
    team_tokens = dict()
    for group in teams_to_tokens:
        team, token = group.rsplit(":", maxsplit=1)
        team = team.replace('\\"', '"')
        team_tokens[team] = token
        logger.info(f'Received token "{token}" for team "{team}"')

    return team_tokens


def create_team_archives(config, vpn_info, tf_output, team_tokens, generated):
    archives = generated / "archives"
    archives.mkdir(parents=True, exist_ok=True)
    team_archive_controller = TeamArchiveController()

    ansible = AnsibleController()
    inventory = ansible.create_or_restore_inventory(config, vpn_info, tf_output)

    for i, team in enumerate(config.teams.teams):
        instance = None
        for vulnbox, info in zip(tf_output.addresses.internal.vulnboxes, inventory.vulnbox_info):
            if vulnbox.number == i:
                instance = InstanceInfo(
                    username=info.team_username,
                    password=info.team_password,
                )
                break

        team_info = TeamInfo(
            number=i,
            name=team.name,
            token=team_tokens[team.name],
            instance=instance,
            game_address=vpn_info.team_configs[i].vulnbox_address,
        )
        team_dir = generated / "teams" / f"team{i:03}"

        archive_path = archives / f"team{i:03}.zip"
        team_archive_controller.create_archive(
            config, team_info, tf_output.addresses, team_dir, archive_path
        )


@cli.command("destroy")
def destroy():
    destroy_impl()


def destroy_impl():
    terraform = TerraformController()
    terraform.destroy()

    generated = REPOSITORY_ROOT / "generated"
    for entry in generated.iterdir():
        if entry.name != ".keep":
            logger.info(f"Removing {entry}")
            if entry.is_file():
                entry.unlink()
            else:
                shutil.rmtree(entry)

    ansible = AnsibleController()
    if ansible.inventory_path.exists():
        logger.info(f"Removing {ansible.inventory_path}")
        ansible.inventory_path.unlink()
