from enum import Enum, auto


class Resource(Enum):
    CONFIG = auto()
    VPN_CONFIGS_SAVED_TO_DISK = auto()
    ADMIN_SSH_KEY = auto()
    ADMIN_SSH_KEY_FILE_SAVED_TO_DISK = auto()
    TERRAFORM_CONFIG_SAVED_TO_DISK = auto()
    ANSIBLE_CONFIGURED = auto()
    VULNBOX_CONFIGS = auto()
    FORCAD_CONFIG = auto()
    FORCAD_CONFIG_FILE_SAVED_TO_DISK = auto()
    TEAM_TOKENS = auto()
    TEAM_ARCHIVES_SAVED_TO_DISK = auto()

    VPN_HOST_IP = auto()
    JURY_HOST_IP = auto()
    BASTION_HOST_IP = auto()
    VULNBOX_HOSTS_IPS = auto()
    JURY_HOST_UP = auto()
    VPN_HOST_UP = auto()
    ALL_VULNBOX_HOSTS_UP = auto()
    VPN_HOST_CONFIGURED = auto()
    JURY_HOST_CONFIGURED = auto()
    ALL_VULNBOX_HOSTS_CONFIGURED = auto()
    FORCAD_STARTED = auto()

    TERRAFORM_DESTROYED = auto()
    FILESYSTEM_CLEANED = auto()
