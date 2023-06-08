# Taken from https://github.com/pomo-mondreganto/OVPNGen/blob/master/config.py
# Modified a bit to fit this project better and work with newer versions of dependencies

import os

from constants.paths import GENERATED_PATH, INTERNAL_PATH

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.join(BASE_DIR, "templates")

PRIVATE_CONFIGS_PATH = INTERNAL_PATH / "vpn"
PUBLIC_CONFIGS_PATH = GENERATED_PATH / "vpn"

TEAM_CLIENT_DIR = PUBLIC_CONFIGS_PATH
VULN_CLIENT_DIR = PRIVATE_CONFIGS_PATH / "vuln" / "client"
JURY_CLIENT_DIR = PRIVATE_CONFIGS_PATH / "jury" / "client"

TEAM_SERVER_DIR = PRIVATE_CONFIGS_PATH / "team" / "server"
VULN_SERVER_DIR = PRIVATE_CONFIGS_PATH / "vuln" / "server"
JURY_SERVER_DIR = PRIVATE_CONFIGS_PATH / "jury" / "server"

TEAM_PORT = 30000
VULN_PORT = 31000
JURY_PORT = 32000
