from enum import Enum, auto


class Resource(Enum):
    SOURCES_PACKED = auto()
    CONFIG = auto()
    VPN_CONFIGS_READY = auto()
    ADMIN_SSH_KEY = auto()
    ADMIN_SSH_KEY_FILE = auto()
    TERRAFORM_CONFIG_READY = auto()
    INFRASTRUCTURE_READY = auto()
    ANSIBLE_INVENTORY_READY = auto()
    VULNBOX_CONFIGS = auto()

    VPN_HOST = auto()
    JURY_HOST = auto()
    BASTION_HOST = auto()
    VULNBOX_HOSTS = auto()
    JURY_HOST_UP = auto()
    VPN_HOST_UP = auto()
    ALL_VULNBOX_HOSTS_UP = auto()
    VPN_HOST_CONFIGURED = auto()
    JURY_HOST_CONFIGURED = auto()
    ALL_VULNBOX_HOSTS_CONFIGURED = auto()

    TERRAFORM_DESTROYED = auto()
    FILESYSTEM_CLEANED = auto()
