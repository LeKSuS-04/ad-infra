import re

from constants.paths import ANSIBLE_PATH
from models.forcad import ForcadTeamToken
from tools import Resource, Syncer, log, task

from .environment import run_with_ansible_env


def run_playbook(playbook_name: str) -> bytes:
    playbook_path = ANSIBLE_PATH / "playbooks" / playbook_name
    return run_with_ansible_env(f"ansible-playbook '{playbook_path}'")


@task(depends_on_boolean=[Resource.VPN_HOST_UP])
def configure_vpn(sync: Syncer):
    run_playbook("vpn_conf.yaml")
    sync.set_resource(Resource.VPN_HOST_CONFIGURED)


@task(depends_on_boolean=[Resource.JURY_HOST_UP, Resource.FORCAD_CONFIG_READY])
def configure_jury(sync: Syncer):
    output = run_playbook("jury_conf.yaml").decode()

    team_tokens_match = re.search(r'"team_tokens\.stdout": "(?P<tokens>.*)"', output)
    if team_tokens_match is None:
        raise ValueError("Can't find team tokens in ForcAD output from Ansible")

    teams_to_tokens = team_tokens_match.group('tokens').split('\\n')
    team_tokens: list[ForcadTeamToken] = []
    for group in teams_to_tokens:
        team, token = group.rsplit(':', maxsplit=1)
        team_tokens.append(
            ForcadTeamToken(
                team_name=team,
                token=token,
            )
        )
        log(f'Received token "{token}" for team "{team}"')

    sync.set_resource(Resource.TEAM_TOKENS, team_tokens)
    sync.set_resource(Resource.JURY_HOST_CONFIGURED)


@task(depends_on_boolean=[Resource.ALL_VULNBOX_HOSTS_UP])
def configure_vulnboxes(sync: Syncer):
    run_playbook("vulnboxes_conf.yaml")
    sync.set_resource(Resource.ALL_VULNBOX_HOSTS_CONFIGURED)
