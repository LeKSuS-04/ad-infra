from ipaddress import IPv4Address
from itertools import count

import yaml
from constants.paths import CONFIG_PATH, TEAMS_CONFIG_PATH
from models import (
    Config,
    LoadedConfig,
    LoadedTeams,
    LoadedTeamsItem,
    Team,
    TerraformConfig,
    VMConfig,
)
from tools import Resource, Syncer, log, task


def create_team(loaded: LoadedTeamsItem, team_number: int) -> Team:
    team_ip = f"10.{80 + team_number // 256}.{team_number % 256}.2"
    return Team(name=loaded.name, game_ip=IPv4Address(team_ip))


@task(depends_on=[])
def load_config(sync: Syncer):
    with open(CONFIG_PATH) as config_file, open(TEAMS_CONFIG_PATH) as teams_file:
        loaded_config = LoadedConfig.parse_obj(yaml.load(config_file, yaml.SafeLoader))
        log("Loaded and validated config.yaml")

        loaded_teams = LoadedTeams.parse_obj(yaml.load(teams_file, yaml.SafeLoader))
        log("Loaded and validated teams.yaml")

    if loaded_config.teams.add_npc:
        loaded_teams.teams.append(LoadedTeamsItem(name="NPC"))

    terraform_config = TerraformConfig(
        yandex_cloud=loaded_config.yandex_cloud,
        vulnbox_count=len(loaded_teams.teams),
        jury_vm=VMConfig(
            cores=4,
            ram_gb=4,
            ssd_gb=20,
        ),
        vpn_vm=VMConfig(
            cores=4,
            ram_gb=4,
            ssd_gb=20,
        ),
        vulnbox_vm=VMConfig(
            cores=4,
            ram_gb=4,
            ssd_gb=20,
        ),
        bastion_vm=VMConfig(
            cores=2,
            ram_gb=2,
            ssd_gb=10,
        ),
    )

    config = Config(
        terraform_config=terraform_config,
        src_dirname=loaded_config.src_dirname,
        game=loaded_config.game,
        forcad_admin=loaded_config.admin,
        tasks=loaded_config.tasks,
        teams=[create_team(loaded, number) for loaded, number in zip(loaded_teams.teams, count(1))],
        players_per_team=loaded_config.teams.players_per_team,
    )

    sync.set_resource(Resource.CONFIG, config)
