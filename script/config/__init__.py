from pathlib import Path

import yaml
from pydantic import BaseModel

from .infra import InfraConfig
from .teams import TeamsConfig


class Config(BaseModel):
    infra: InfraConfig
    teams: TeamsConfig


def load_config(infra_path: Path, teams_path: Path) -> Config:
    with open(infra_path) as f:
        infra = InfraConfig(**yaml.safe_load(f))
        InfraConfig.model_validate(infra)

    with open(teams_path) as f:
        teams = TeamsConfig(**yaml.safe_load(f))
        TeamsConfig.model_validate(teams)

    return Config(infra=infra, teams=teams)
