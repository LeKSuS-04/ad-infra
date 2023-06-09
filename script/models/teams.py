from ipaddress import IPv4Address
from pathlib import Path

from pydantic import BaseModel


class VulnboxConfig(BaseModel):
    real_ip: IPv4Address
    game_ip: IPv4Address
    local_vpn_config_path: Path
    username: str
    password: str
