from . import ansible, terraform, vpn
from .clean_filesystem import clean_filesystem
from .get_ssh_keys import get_ssh_keys
from .load_config import load_config
from .map_teams_to_vulnbox_configs import map_teams_to_vulnbox_configs
from .pack_team_archives import pack_team_archives
from .save_forcad_config import save_forcad_config

TASK_LIST = [
    clean_filesystem,
    get_ssh_keys,
    load_config,
    map_teams_to_vulnbox_configs,
    pack_team_archives,
    save_forcad_config,
    #
    ansible.configure_jury,
    ansible.configure_vpn,
    ansible.configure_vulnboxes,
    ansible.ping_all_hosts,
    ansible.prepare_inventory,
    #
    terraform.deploy_infrastructure,
    terraform.destroy_infrastructure,
    terraform.save_terraform_config,
    #
    vpn.create_configs,
]
