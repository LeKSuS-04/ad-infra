from models import VulnboxConfig


def to_ansible_vunlbox_config(teams_to_vulnboxes: dict[str, VulnboxConfig]):
    ansible_vulnbox_configs = dict()
    for host in teams_to_vulnboxes.values():
        ansible_vulnbox_configs[host.real_ip] = {
            "vpn_file": host.local_vpn_config_path,
            "user": host.username,
            "password": host.password,
        }
    return ansible_vulnbox_configs
