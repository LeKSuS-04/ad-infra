# Taken from https://github.com/pomo-mondreganto/OVPNGen/blob/master/config.py
# Modified a bit to fit this project better and work with newer versions of dependencies

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.join(BASE_DIR, "templates")

TEAM_PORT = 30000
VULN_PORT = 31000
JURY_PORT = 32000
