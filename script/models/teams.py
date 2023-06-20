from ipaddress import IPv4Address
from pathlib import Path

from pydantic import BaseModel


class VulnboxConfig(BaseModel):
    real_ip: IPv4Address
    game_ip: IPv4Address
    local_vpn_config_path: Path
    username: str
    password: str


class TeamConfig(BaseModel):
    name: str
    vulnbox_ip: IPv4Address
    vulnbox_username: str
    vulnbox_password: str
    token: str


TeamTokens = dict[str, str]
