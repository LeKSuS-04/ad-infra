from pathlib import Path

from pydantic import BaseModel, PositiveInt, conint

from .loaded_config import (
    ForcadAdminConfig,
    ForcadTaskConfig,
    GameConfig,
    LoadedTeam,
    YandexCloudConfig,
)


class VMConfig(BaseModel):
    cores: conint(gt=0, multiple_of=2)  # type: ignore
    ram_gb: conint(gt=0, multiple_of=2)  # type: ignore
    ssd_gb: conint(gt=0)  # type: ignore


class TerraformConfig(BaseModel):
    yandex_cloud: YandexCloudConfig
    vulnbox_count: PositiveInt
    jury_vm: VMConfig
    vpn_vm: VMConfig
    vulnbox_vm: VMConfig
    bastion_vm: VMConfig


class Config(BaseModel):
    """Configuration, created by merging LoadedConfig, LoadedTeams and adding a bit of magic."""

    terraform_config: TerraformConfig
    src_dirname: Path
    game: GameConfig
    tasks: list[ForcadTaskConfig]
    forcad_admin: ForcadAdminConfig
    teams: list[LoadedTeam]
    players_per_team: PositiveInt
    archive_password: str | None
    readme_template: str
