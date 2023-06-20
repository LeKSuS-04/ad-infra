from datetime import datetime
from ipaddress import IPv4Address

from pydantic import BaseModel

from .config import Config, ForcadAdminConfig, ForcadTaskConfig
from .teams import VulnboxConfig


class ForcadTeamConfig(BaseModel):
    name: str
    ip: IPv4Address
    highlighted: bool | None = None


class ForcadGameConfig(BaseModel):
    mode: str = "classic"
    round_time: int
    start_time: datetime
    timezone: str
    default_score: int
    flag_lifetime: int
    game_hardness: float = 10.0
    inflation: bool = True


class ForcadConfig(BaseModel):
    admin: ForcadAdminConfig
    game: ForcadGameConfig
    teams: list[ForcadTeamConfig]
    tasks: list[ForcadTaskConfig]

    @classmethod
    def from_config(cls, config: Config, vulnbox_configs: dict[str, VulnboxConfig]):
        game = ForcadGameConfig(
            round_time=config.game.round_time,
            start_time=config.game.start_time,
            timezone=config.game.timezone,
            default_score=config.game.default_score,
            flag_lifetime=config.game.flag_lifetime,
            game_hardness=config.game.game_hardness,
            inflation=config.game.inflation,
        )

        teams = [
            ForcadTeamConfig(name=team_name, ip=vulnbox_config.game_ip)
            for team_name, vulnbox_config in vulnbox_configs.items()
        ]

        return ForcadConfig(
            admin=config.forcad_admin,
            tasks=config.tasks,
            game=game,
            teams=teams,
        )
