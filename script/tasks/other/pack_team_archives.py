from pathlib import Path
from zipfile import ZipFile

from jinja2 import Environment
from models import Config, ForcadConfig, TeamConfig, TeamTokens, VulnboxConfig
from tools import Resource, Syncer, task
from tools.paths import team_archive_path, vpn_team_client_path

_JINJA_ENV = Environment()


def _generate_readme(
    team_name: str,
    vulnbox: VulnboxConfig,
    config: Config,
    forcad_config: ForcadConfig,
    team_tokens: TeamTokens,
    public_jury_ip: str,
):
    team_config = TeamConfig(
        name=team_name,
        vulnbox_ip=vulnbox.game_ip,
        vulnbox_username=vulnbox.username,
        vulnbox_password=vulnbox.password,
        token=team_tokens[team_name],
    )

    readme_template = _JINJA_ENV.from_string(config.readme_template)
    readme_content = readme_template.render(
        team=team_config,
        config=config,
        forcad=forcad_config,
        public_jury_ip=public_jury_ip,
    )

    return readme_content


@task(
    depends_on=[
        Resource.CONFIG,
        Resource.VULNBOX_CONFIGS,
        Resource.FORCAD_CONFIG,
        Resource.TEAM_TOKENS,
        Resource.JURY_HOST_PUBLIC_IP,
    ],
    creates=[Resource.TEAM_ARCHIVES_SAVED_TO_DISK],
)
def pack_team_archives(
    sync: Syncer,
    config: Config,
    vulnbox_configs: dict[str, VulnboxConfig],
    forcad_config: ForcadConfig,
    team_tokens: TeamTokens,
    jury_host: str,
):
    for team_num, (team_name, vulnbox) in enumerate(vulnbox_configs.items(), start=1):
        archive_path = team_archive_path(team_name, team_num)
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        with ZipFile(archive_path, "w") as zip:
            readme_content = _generate_readme(
                team_name, vulnbox, config, forcad_config, team_tokens, jury_host
            )
            zip.writestr("README.md", readme_content)

            team_vpn_clients = [
                vpn_team_client_path(team_num, player_num)
                for player_num in range(1, config.players_per_team + 1)
            ]
            for vpn_client in team_vpn_clients:
                zip.write(vpn_client, Path("vpn") / vpn_client.name)

            if config.archive_password is not None:
                zip.setpassword(config.archive_password.encode())

    sync.set_resource(Resource.TEAM_ARCHIVES_SAVED_TO_DISK)
