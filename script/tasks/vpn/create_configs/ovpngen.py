# Taken from https://github.com/pomo-mondreganto/OVPNGen/blob/master/gen.py
# Modified a bit to fit this project better and work with newer versions of dependencies

import os

from . import config, generator


def initialized():
    paths = (config.PRIVATE_CONFIGS_PATH, config.PUBLIC_CONFIGS_PATH)
    return any(path.exists() for path in paths)


def initialize():
    if initialized():
        raise EnvironmentError("OVPN output directories already initialized")

    os.makedirs(config.TEAM_SERVER_DIR)
    os.makedirs(config.VULN_SERVER_DIR)
    os.makedirs(config.JURY_SERVER_DIR)

    os.makedirs(config.TEAM_CLIENT_DIR)
    os.makedirs(config.VULN_CLIENT_DIR)
    os.makedirs(config.JURY_CLIENT_DIR)


def generate(team_count, per_team, vpn_server):
    cg = generator.ConfigGenerator(vpn_server=vpn_server)
    team_list = list(range(1, team_count + 1))
    cg.generate_for_teams(team_list=team_list, per_team=per_team)
    cg.generate_for_vulns(team_list)
    cg.generate_for_jury()
