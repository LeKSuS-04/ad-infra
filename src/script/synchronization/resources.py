from enum import Enum, auto


class Resource(Enum):
    CONFIG = auto()
    ADMIN_SSH_KEY = auto()
    VPN_ADDRESS = auto()
    JURY_ADDRESS = auto()
    BASTION_ADDRESS = auto()
    INFRASTRUCTURE_READY = auto()