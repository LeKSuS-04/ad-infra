from enum import Enum, auto


class Resource(Enum):
    SOURCES_PACKED = auto()
    CONFIG = auto()
    OVPN_CONFIGS_READY = auto()
    ADMIN_SSH_KEY = auto()
    ADMIN_SSH_KEY_FILE = auto()
    VPN_HOST = auto()
    JURY_HOST = auto()
    BASTION_HOST = auto()
    VULNBOX_HOSTS = auto()
    TERRAFORM_CONFIG_READY = auto()
    INFRASTRUCTURE_READY = auto()
    ANSIBLE_INVENTORY_READY = auto()

    TERRAFORM_DESTROYED = auto()
    FILESYSTEM_CLEANED = auto()
