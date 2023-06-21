import json
from ipaddress import IPv4Address
from random import choices
from string import ascii_lowercase, digits

from models import Config, Team, VulnboxConfig
from tools import Resource, Syncer, log, task
from tools.paths import TEAMS_TO_VULNBOX_CONFIG_PATH, vpn_vunlbox_client_path


def _random_string(alphabet: str = ascii_lowercase + digits, length: int = 32) -> str:
    return "".join(choices(alphabet, k=length))


def _generate(teams: list[Team], vulnbox_hosts: list[str]) -> dict[str, VulnboxConfig]:
    vulnbox_configs: dict[str, VulnboxConfig] = dict()

    for num, (team, host) in enumerate(zip(teams, vulnbox_hosts), start=1):
        game_ip = f"10.{80 + num // 256}.{num % 256}.2"
        vunlbox_config = VulnboxConfig(
            real_ip=IPv4Address(host),
            local_vpn_config_path=vpn_vunlbox_client_path(num),
            username="team",
            password=_random_string(),
            # There is a concern that vulnbox game_ip format might be changed in future (although
            # very unlikely). So this probably shouldn't be calculated in two places (ovpngen
            # and here), but saved while generating VPN configs and tied to VPN config file somehow.
            # XXX: probably needs refactoring, read above for details.
            game_ip=IPv4Address(game_ip),
        )
        vulnbox_configs[team.name] = vunlbox_config
        log(f'Vulnbox {host} (in-game address {game_ip}) was assigned to team "{team.name}"')

    return vulnbox_configs


@task(
    depends_on=[Resource.CONFIG, Resource.VULNBOX_HOSTS_IPS],
    depends_on_boolean=[Resource.VPN_CONFIGS_SAVED_TO_DISK],
    creates=[Resource.VULNBOX_CONFIGS],
)
def map_teams_to_vulnbox_configs(sync: Syncer, config: Config, vulnbox_hosts: list[str]):
    if TEAMS_TO_VULNBOX_CONFIG_PATH.exists():
        log(f"Found existing vulnbox configs at {TEAMS_TO_VULNBOX_CONFIG_PATH}")

        with open(TEAMS_TO_VULNBOX_CONFIG_PATH) as f:
            data = json.load(f)
            vulnbox_configs = {
                team_name: VulnboxConfig(**vulnbox_config)
                for team_name, vulnbox_config in data.items()
            }
        sync.set_resource(Resource.VULNBOX_CONFIGS, vulnbox_configs)
    else:
        log("Generating vulnbox configs and mapping them to teams")

        vulnbox_configs = _generate(config.teams, vulnbox_hosts)
        sync.set_resource(Resource.VULNBOX_CONFIGS, vulnbox_configs)

        with open(TEAMS_TO_VULNBOX_CONFIG_PATH, "w") as f:
            json_mapping = {
                team_name: json.loads(vulnbox_config.json())
                for team_name, vulnbox_config in vulnbox_configs.items()
            }
            json.dump(json_mapping, f)
