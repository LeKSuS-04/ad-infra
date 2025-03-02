from dataclasses import dataclass
from pathlib import Path

from config import Config
from controllers.terraform import Addresses
from jinja2 import Environment
from util import get_logger
from util.process import run_process


@dataclass
class InstanceInfo:
    username: str
    password: str


@dataclass
class TeamInfo:
    number: int
    name: str
    token: str
    instance: InstanceInfo | None
    game_address: str


class TeamArchiveController:
    def __init__(self):
        self._logger = get_logger("team-archive-controller")
        self._jinja2_env = Environment()

    def create_archive(
        self,
        config: Config,
        team_info: TeamInfo,
        addresses: Addresses,
        team_dir: Path,
        archive_path: Path,
    ):
        self._logger.info(f"Creating archive for team {team_info.name}")

        readme = self._render_readme(config, team_info, addresses)
        readme_path = team_dir / "README.md"
        readme_path.write_text(readme)

        args = ["zip"]
        if config.infra.teams.archive_password:
            args.extend(["--password", config.infra.teams.archive_password])
        args.extend(["-r", str(archive_path.absolute()), str(team_dir.name)])

        run_process(args, cwd=team_dir.parent)

    def _render_readme(self, config: Config, team_info: TeamInfo, addresses: Addresses) -> str:
        template = self._jinja2_env.from_string(config.infra.teams.readme_template)

        return template.render(
            config=config,
            team=team_info,
            addresses=addresses,
        )
