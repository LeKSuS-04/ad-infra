from ipaddress import IPv4Address
from random import choices
from string import ascii_lowercase, digits

from constants.paths import INTERNAL_PATH
from models import VulnboxConfig
from tools import Resource, Syncer, task


def _random_string(alphabet: str = ascii_lowercase + digits, length: int = 32) -> str:
    return "".join(choices(alphabet, k=length))


@task(depends_on=[Resource.VULNBOX_HOSTS], depends_on_boolean=[Resource.VPN_CONFIGS_READY])
def generate_vulnbox_configs(sync: Syncer, vulnbox_hosts: list[str]):
    vulnbox_configs: list[VulnboxConfig] = []

    for i, host in enumerate(vulnbox_hosts, start=1):
        vunlbox_config = VulnboxConfig(
            real_ip=IPv4Address(host),
            local_vpn_config_path=INTERNAL_PATH / "vpn" / "vuln" / "client" / f"vuln{i:03}.ovpn",
            username="team",
            password=_random_string(),
            # We can do this because Resource.VULNBOX_HOSTS is set according to terraaform output,
            # which provides IPs of vulnboxes in correct order. Since all lists are ordered,
            # i-th vulnbox IP will belong to i-th team.
            # Other concern is that vulnbox game_ip format might be changed in future (although
            # very unlikely). So this probably shouldn't be calculated in two places (ovpngen
            # and here), but saved while generating VPN configs and tied to VPN config file.
            # XXX: probably needs refactoring, read above for details.
            game_ip=IPv4Address(f"10.{80 + i // 256}.{i % 256}.2"),
        )
        vulnbox_configs.append(vunlbox_config)

    sync.set_resource(Resource.VULNBOX_CONFIGS, vulnbox_configs)
