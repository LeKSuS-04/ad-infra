from pathlib import Path

from models.config import Config
from constants.paths import GENERATED_PATH
from utils.sync.resources import Resource
from utils.sync import Synchronizator, task
from utils.process import process
from utils.logger import log


@task(depends_on=[Resource.CONFIG, Resource.VPN_HOST])
def ovpngen_create_configs(sync: Synchronizator, config: Config, vpn_host: str):
    script = Path.cwd() / 'OVPNGen' / 'gen.py'
    process(
        f'{script} --server {vpn_host} --jury --vuln --team --teams {len(config.teams)} --per-team {config.players_per_team}',
        cwd=GENERATED_PATH,
    )
    sync.set_resource(Resource.OVPN_CONFIGS_READY)
