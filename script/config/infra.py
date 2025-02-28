from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, conint


class YandexCloudConfig(BaseModel):
    folder_id: str
    zone: Literal["ru-central1-a"] | Literal["ru-central1-b"] | Literal["ru-central1-d"]


class CloudflareConfig(BaseModel):
    zone_id: str


class SshConfig(BaseModel):
    username: str
    private_key_path: Path
    public_keys: list[str]


class VMConfig(BaseModel):
    cores: conint(gt=0, multiple_of=2)  # type: ignore
    ram_gb: conint(gt=0, multiple_of=2)  # type: ignore
    disk_type: Literal["network-hdd"] | Literal["network-ssd"]
    disk_size_gb: conint(gt=0)  # type: ignore


class VMWithSubdomainConfig(VMConfig):
    subdomain: str


class ResourcesPerVMConfig(BaseModel):
    jury: VMWithSubdomainConfig
    vpn: VMWithSubdomainConfig
    bastion: VMWithSubdomainConfig
    container_registry: VMWithSubdomainConfig
    monitoring: VMWithSubdomainConfig
    vulnbox: VMConfig


class RepositoryConfig(BaseModel):
    services_path: Path
    checkers_path: Path


class GameConfig(BaseModel):
    round_time: int
    start_time: datetime
    timezone: str
    default_score: int
    flag_lifetime: int
    game_hardness: float
    inflation: bool


class CheckerConfig(BaseModel):
    name: str
    checker: Path
    checker_timeout: int
    checker_type: str
    puts: int
    gets: int
    places: int
    env_path: str | None = None


class AdminCredentialsConfig(BaseModel):
    username: str
    password: str


class ForcadConfig(BaseModel):
    admin_creds: AdminCredentialsConfig
    game: GameConfig
    checkers: list[CheckerConfig]


class TeamsConfig(BaseModel):
    players_per_team: int
    archive_password: str | None
    readme_template: str


class InfraConfig(BaseModel):
    yandex_cloud: YandexCloudConfig
    cloudflare: CloudflareConfig
    ssh: SshConfig
    resources: ResourcesPerVMConfig
    repository: RepositoryConfig
    forcad: ForcadConfig
    teams: TeamsConfig
