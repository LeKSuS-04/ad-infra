import yaml
from models import (
    Config,
    LoadedConfig,
    LoadedTeams,
    Team,
    TerraformConfig,
)
from tools import Resource, Syncer, log, task
from tools.paths import CONFIG_PATH, TEAMS_CONFIG_PATH

from .resource_manager import ResourceManager


@task(depends_on=[], creates=[Resource.CONFIG])
def load_config(sync: Syncer):
    with open(CONFIG_PATH) as config_file, open(TEAMS_CONFIG_PATH) as teams_file:
        loaded_config = LoadedConfig.parse_obj(yaml.load(config_file, yaml.SafeLoader))
        log("Loaded and validated config.yaml")

        loaded_teams = LoadedTeams.parse_obj(yaml.load(teams_file, yaml.SafeLoader))
        log("Loaded and validated teams.yaml")

    if loaded_config.teams.add_npc:
        loaded_teams.teams.append(Team(name="NPC"))

    resource_master = ResourceManager(loaded_config.virtual_machines)
    terraform_config = TerraformConfig(
        yandex_cloud=loaded_config.yandex_cloud,
        vulnbox_count=len(loaded_teams.teams),
        jury_vm=resource_master.get_jury_resources(loaded_config, loaded_teams.teams),
        vpn_vm=resource_master.get_vpn_resources(loaded_config, loaded_teams.teams),
        vulnbox_vm=resource_master.get_vulnbox_resources(loaded_config, loaded_teams.teams),
        bastion_vm=resource_master.get_bastion_resources(loaded_config, loaded_teams.teams),
    )

    config = Config(
        terraform_config=terraform_config,
        src_dirname=loaded_config.src_dirname,
        game=loaded_config.game,
        forcad_admin=loaded_config.admin,
        tasks=loaded_config.tasks,
        teams=loaded_teams.teams,
        players_per_team=loaded_config.teams.players_per_team,
        archive_password=loaded_config.teams.archive_password,
        readme_template=loaded_config.teams.readme_template,
    )

    sync.set_resource(Resource.CONFIG, config)
