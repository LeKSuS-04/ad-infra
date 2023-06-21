from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PositiveInt, conint, validator


class YandexCloudConfig(BaseModel):
    folder_id: str
    iam_token: str
    zone: Literal["ru-central1-a"] | Literal["ru-central1-b"] | Literal["ru-central1-c"]


class LoadedConfigTeams(BaseModel):
    players_per_team: PositiveInt
    add_npc: bool
    archive_password: str | None = None
    readme_template: str


class GameConfig(BaseModel):
    round_time: int
    start_time: datetime
    timezone: str
    default_score: int
    flag_lifetime: int
    game_hardness: float
    inflation: bool


class ForcadTaskConfig(BaseModel):
    name: str
    checker: Path
    checker_timeout: int
    checker_type: str
    puts: int
    gets: int
    places: int
    env_path: str | None = None


class ForcadAdminConfig(BaseModel):
    username: str
    password: str


class ResourceEstimationBehaviour(Enum):
    LOW = "tiny"
    MEDIUM = "auto"
    BIG = "generous"


class VMResources(BaseModel):
    cores: conint(gt=0, multiple_of=2) | ResourceEstimationBehaviour  # type: ignore
    ram_gb: conint(gt=0, multiple_of=2) | ResourceEstimationBehaviour  # type: ignore
    ssd_gb: conint(gt=0) | ResourceEstimationBehaviour  # type: ignore


class ResourcesPerVMConfig(BaseModel):
    jury: VMResources | ResourceEstimationBehaviour
    vpn: VMResources | ResourceEstimationBehaviour
    vulnbox: VMResources | ResourceEstimationBehaviour
    bastion: VMResources | ResourceEstimationBehaviour


class LoadedConfig(BaseModel):
    """Structure of config.yaml."""

    yandex_cloud: YandexCloudConfig
    src_dirname: Path
    virtual_machines: ResourcesPerVMConfig | ResourceEstimationBehaviour
    admin: ForcadAdminConfig
    game: GameConfig
    tasks: list[ForcadTaskConfig]
    teams: LoadedConfigTeams


class Team(BaseModel):
    name: str


class LoadedTeams(BaseModel):
    """Structure of teams.yaml."""

    teams: list[Team]

    @validator("teams")
    def must_be_unique(cls, teams: list[Team]):  # noqa: N805
        for team in teams:
            if list(map(lambda t: t.name == team.name, teams)).count(True) > 1:
                raise ValueError(f'Team "{team.name}" is registered multiple times')
        return teams
