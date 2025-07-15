from pathlib import Path

import yaml
from config import Config
from controllers.wireguard import VpnInfo
from util.log import get_logger


class ForcadController:
    def __init__(self):
        self._logger = get_logger("forcad-controller")

    def save_forcad_config(self, config: Config, vpn_info: VpnInfo, output_path: Path):
        forcad_config = {
            "game": {
                "round_time": config.infra.forcad.game.round_time,
                "start_time": config.infra.forcad.game.start_time,
                "timezone": config.infra.forcad.game.timezone,
                "default_score": config.infra.forcad.game.default_score,
                "flag_lifetime": config.infra.forcad.game.flag_lifetime,
                "game_hardness": config.infra.forcad.game.game_hardness,
                "inflation": config.infra.forcad.game.inflation,
            },
            "teams": [
                {
                    "name": team.name,
                    "ip": team_config.vulnbox_address,
                    "highlighted": team.highlighted,
                }
                for team, team_config in zip(config.teams.teams, vpn_info.team_vpn_infos)
            ],
            "admin": {
                "username": config.infra.forcad.admin_creds.username,
                "password": config.infra.forcad.admin_creds.password,
            },
            "tasks": [checker.model_dump(mode="json") for checker in config.infra.forcad.checkers],
        }

        self._logger.info(f"Saving Forcad config to {output_path}")
        output_path.write_text(yaml.dump(forcad_config, indent=2))
