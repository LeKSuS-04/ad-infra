from pathlib import Path

from models import Config, VulnboxConfig
from tools.paths import VPN_JURY_SERVER_PATH, vpn_team_server_path, vpn_vunlbox_server_path


def to_ansible_vunlbox_config(teams_to_vulnboxes: dict[str, VulnboxConfig]):
    ansible_vulnbox_configs = dict()
    for host in teams_to_vulnboxes.values():
        ansible_vulnbox_configs[host.real_ip] = {
            "vpn_file": host.local_vpn_config_path,
            "user": host.username,
            "password": host.password,
        }
    return ansible_vulnbox_configs


def get_all_vpn_server_paths(config: Config) -> list[Path]:
    paths = [VPN_JURY_SERVER_PATH]

    for team_num in range(1, len(config.teams) + 1):
        paths.append(vpn_team_server_path(team_num))
        paths.append(vpn_vunlbox_server_path(team_num))

    return paths
