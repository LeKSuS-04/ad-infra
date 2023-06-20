from ipaddress import IPv4Address
from random import choices
from string import ascii_lowercase, digits

from models import Config, VulnboxConfig
from tools import Resource, Syncer, task
from tools.paths import vpn_vunlbox_client_path


def _random_string(alphabet: str = ascii_lowercase + digits, length: int = 32) -> str:
    return "".join(choices(alphabet, k=length))


@task(
    depends_on=[Resource.CONFIG, Resource.VULNBOX_HOSTS_IPS],
    depends_on_boolean=[Resource.VPN_CONFIGS_SAVED_TO_DISK],
    creates=[Resource.VULNBOX_CONFIGS],
)
def map_teams_to_vulnbox_configs(sync: Syncer, config: Config, vulnbox_hosts: list[str]):
    vulnbox_configs: dict[str, VulnboxConfig] = dict()

    for num, (team, host) in enumerate(zip(config.teams, vulnbox_hosts), start=1):
        vunlbox_config = VulnboxConfig(
            real_ip=IPv4Address(host),
            local_vpn_config_path=vpn_vunlbox_client_path(num),
            username="team",
            password=_random_string(),
            # There is a concern that vulnbox game_ip format might be changed in future (although
            # very unlikely). So this probably shouldn't be calculated in two places (ovpngen
            # and here), but saved while generating VPN configs and tied to VPN config file somehow.
            # XXX: probably needs refactoring, read above for details.
            game_ip=IPv4Address(f"10.{80 + num // 256}.{num % 256}.2"),
        )
        vulnbox_configs[team.name] = vunlbox_config

    sync.set_resource(Resource.VULNBOX_CONFIGS, vulnbox_configs)
