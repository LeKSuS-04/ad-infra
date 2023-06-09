from models.config import Config
from tools import Resource, Syncer, log, task

from . import ovpngen


def generate_if_not_exist(config: Config, vpn_host: str):
    if ovpngen.initialized():
        log("OpenVPN configs already exist; skipping generation")
        return

    ovpngen.initialize()
    log("Initialized directories")
    ovpngen.generate(
        team_count=len(config.teams),
        per_team=config.players_per_team,
        vpn_server=vpn_host,
    )


@task(depends_on=[Resource.CONFIG, Resource.VPN_HOST])
def create_configs(sync: Syncer, *resources):
    generate_if_not_exist(*resources)
    sync.set_resource(Resource.VPN_CONFIGS_READY)
