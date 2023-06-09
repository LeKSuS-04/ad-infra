from pathlib import Path

import yaml
from models import (
    Config,
    LoadedConfig,
    LoadedTeams,
    LoadedTeamsItem,
    NetworkConfig,
    Team,
    TerraformConfig,
    VMConfig,
)
from tools import Resource, Syncer, log, task


def create_team(loaded: LoadedTeamsItem) -> Team:
    return Team(name=loaded.name)


@task(depends_on=[])
def load_config(sync: Syncer):
    config_path = Path.cwd() / "config.yaml"
    teams_path = Path.cwd() / "teams.yaml"

    with open(config_path) as config_file, open(teams_path) as teams_file:
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
        src_path=loaded_config.src_path,
        network=loaded_config.network,
        teams=list(map(create_team, loaded_teams.teams)),
        players_per_team=loaded_config.teams.players_per_team,
    )

    sync.set_resource(Resource.CONFIG, config)
