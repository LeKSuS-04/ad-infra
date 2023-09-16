from pathlib import Path
from random import choice
from string import ascii_letters, digits

from .chars_to_ascii_alphanum import normalize_char


def random_string(length: int = 32, alpha: str = ascii_letters + digits):
    return "".join(choice(alpha) for _ in range(length))


################# GENERAL #################

CWD = Path.cwd()
ROOT = Path("/")

CONFIG_PATH = CWD / "config.yaml"
TEAMS_CONFIG_PATH = CWD / "teams.yaml"
TEMPORARY_DIR = ROOT / "tmp"

################# ANSIBLE #################

ANSIBLE_DIR = CWD / "ansible"
ANSIBLE_CONFIG_PATH = ANSIBLE_DIR / "ansible.cfg"
ANSIBLE_INVENTORY_PATH = ANSIBLE_DIR / "inventory.yaml"
ANSIBLE_PLAYBOOKS_DIR = ANSIBLE_DIR / "playbooks"
ANSIBLE_JURY_CONF_PLAYBOOK_PATH = ANSIBLE_PLAYBOOKS_DIR / "jury_conf.yaml"
ANSIBLE_JURY_RUN_PLAYBOOK_PATH = ANSIBLE_PLAYBOOKS_DIR / "jury_run.yaml"
ANSIBLE_VPN_CONF_PLAYBOOK_PATH = ANSIBLE_PLAYBOOKS_DIR / "vpn_conf.yaml"
ANSIBLE_VULNBOXES_CONF_PLAYBOOK_PATH = ANSIBLE_PLAYBOOKS_DIR / "vulnboxes_conf.yaml"
ANSIBLE_CONTAINER_REGISTRY_CONF_PLAYBOOK_PATH = (
    ANSIBLE_PLAYBOOKS_DIR / "container_registry_conf.yaml"
)

################# TERRAFORM #################

TERRAFORM_DIR = CWD / "terraform"
TERRAFORM_CONFIG_PATH = TERRAFORM_DIR / "variables.auto.tfvars.json"
TERRAFORM_CLOUD_INIT_CONFIG_PATH = TERRAFORM_DIR / "cloud-init.yaml"


################# SERVICES #################

SERVICES_DIR = CWD / "services"
CONTAINER_REGISTRY_SERVICE_DIR = SERVICES_DIR / "container_registry"

################# PUBLIC #################

PUBLIC_GENERATED_DIR = CWD / "generated"

PRIV_SSH_KEY_FILE_PATH = PUBLIC_GENERATED_DIR / "id_ecdsa"
PUB_SSH_KEY_FILE_PATH = PUBLIC_GENERATED_DIR / "id_ecdsa.pub"

FORCAD_CONFIG_PATH = PUBLIC_GENERATED_DIR / "forcad.yaml"

PUBLIC_VPN_DIR = PUBLIC_GENERATED_DIR / "vpn"


def _normalize_team_name(team_name: str) -> str:
    normalized_team_name = ""
    for char in team_name:
        normalized_team_name += normalize_char(char)
    return normalized_team_name


def team_archive_path(team_name: str, team_num: int) -> Path:
    normalized_team_name = _normalize_team_name(team_name)
    zipfile_name = f"{normalized_team_name}.team{team_num:03}.zip"
    return PUBLIC_GENERATED_DIR / "dist" / zipfile_name


################# PRIVATE #################

PRIVATE_GENERATED_DIR = ROOT / "private"

TEAMS_TO_VULNBOX_CONFIG_PATH = PRIVATE_GENERATED_DIR / "vulnbox_configs.json"

PRIVATE_VPN_DIR = PRIVATE_GENERATED_DIR / "vpn"
VPN_JURY_CLIENT_PATH = PRIVATE_VPN_DIR / "client" / "jury.ovpn"
VPN_JURY_SERVER_PATH = PRIVATE_VPN_DIR / "server" / "jury.conf"


def vpn_vunlbox_client_path(vunlbox_num: int) -> Path:
    return PRIVATE_VPN_DIR / "client" / f"vuln{vunlbox_num:03}.ovpn"


def vpn_vunlbox_server_path(vulnbox_num: int) -> Path:
    return PRIVATE_VPN_DIR / "server" / f"vuln{vulnbox_num:03}.conf"


def vpn_team_client_path(team_num: int, player_num: int) -> Path:
    return PRIVATE_VPN_DIR / "client" / f"team{team_num:03}_{player_num}.ovpn"


def vpn_team_server_path(team_num: int) -> Path:
    return PRIVATE_VPN_DIR / "server" / f"team{team_num:03}.conf"


ANSIBLE_RETRY_FILES_DIR = PRIVATE_GENERATED_DIR / "ansible_retry"

DOCKER_DAEMON_CONFIG_PATH = PRIVATE_GENERATED_DIR / "docker.json"

################# RESOURCES #################

RESOURCES_PATH = CWD / "resources"


def checkers_dir(src_dirname: Path) -> Path:
    return RESOURCES_PATH / src_dirname / "checkers"


def services_dir(src_dirname: Path) -> Path:
    return RESOURCES_PATH / src_dirname / "services"
