import yaml
from pathlib import Path

from models import (
    LoadedConfig,
    LoadedTeams,
    Config,
    Team,
    LoadedTeamsItem,
    TerraformConfig,
    VMConfig,
)
from synchronization import Synchronizator, task
from synchronization.resources import Resource
from utils.logger import log


def create_team(loaded: LoadedTeamsItem) -> Team:
    return Team(name=loaded.name)


@task(depends_on=[])
def load_config(sync: Synchronizator):
    config_path = Path.cwd() / 'config.yaml'
    teams_path = Path.cwd() / 'teams.yaml'

    with open(config_path, 'r') as config_file, open(teams_path, 'r') as teams_file:
        loaded_config = LoadedConfig.parse_obj(yaml.load(config_file, yaml.SafeLoader))
        log('loaded and validated config.yaml')

        loaded_teams = LoadedTeams.parse_obj(yaml.load(teams_file, yaml.SafeLoader))
        log('loaded and validated teams.yaml')

    if loaded_config.teams.add_npc:
        loaded_teams.teams.append(LoadedTeamsItem(name='NPC'))

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
        teams=list(map(create_team, loaded_teams.teams)),
        players_per_team=loaded_config.teams.players_per_team,
    )

    sync.set_resource(Resource.CONFIG, config)
