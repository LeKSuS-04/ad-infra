from enum import Enum, auto


class Resource(Enum):
    SOURCES_PACKED = auto()
    CONFIG = auto()
    ADMIN_SSH_KEY = auto()
    VPN_ADDRESS = auto()
    JURY_ADDRESS = auto()
    BASTION_ADDRESS = auto()
    VULNBOX_INTERNAL_ADDRESSES = auto()
    INFRASTRUCTURE_READY = auto()
