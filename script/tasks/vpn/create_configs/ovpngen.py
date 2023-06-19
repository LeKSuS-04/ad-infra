# Taken from https://github.com/pomo-mondreganto/OVPNGen/blob/master/gen.py
# Modified a bit to fit this project better and work with newer versions of dependencies

from pathlib import Path

from models import Config
from tools.paths import (
    VPN_JURY_CLIENT_PATH,
    VPN_JURY_SERVER_PATH,
    vpn_team_client_path,
    vpn_team_server_path,
    vpn_vunlbox_client_path,
    vpn_vunlbox_server_path,
)

from . import generator


def initialized():
    # All configs are generated at once, so we can check if all they've
    # been initialized just by checking existance of one of them.
    return VPN_JURY_CLIENT_PATH.exists()


def _ensure_file_directory_exists(file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)


def initialize(config: Config):
    if initialized():
        raise OSError("OVPN output directories already initialized")

    _ensure_file_directory_exists(VPN_JURY_CLIENT_PATH)
    _ensure_file_directory_exists(VPN_JURY_SERVER_PATH)

    for team_num in range(1, len(config.teams) + 1):
        _ensure_file_directory_exists(vpn_vunlbox_client_path(team_num))
        _ensure_file_directory_exists(vpn_vunlbox_server_path(team_num))
        _ensure_file_directory_exists(vpn_team_server_path(team_num))
        for player_num in range(1, config.players_per_team + 1):
            _ensure_file_directory_exists(vpn_team_client_path(team_num, player_num))


def generate(team_count, per_team, vpn_server):
    cg = generator.ConfigGenerator(vpn_server=vpn_server)
    team_list = list(range(1, team_count + 1))
    cg.generate_for_teams(team_list=team_list, per_team=per_team)
    cg.generate_for_vulns(team_list)
    cg.generate_for_jury()
