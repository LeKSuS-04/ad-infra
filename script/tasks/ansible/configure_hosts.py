import re
from pathlib import Path

from models import TeamTokens
from tools import Resource, Syncer, log, task
from tools.paths import (
    ANSIBLE_JURY_CONF_PLAYBOOK_PATH,
    ANSIBLE_JURY_RUN_PLAYBOOK_PATH,
    ANSIBLE_VPN_CONF_PLAYBOOK_PATH,
    ANSIBLE_VULNBOXES_CONF_PLAYBOOK_PATH,
)

from .environment import run_with_ansible_env


def _run_playbook(playbook_path: Path) -> bytes:
    return run_with_ansible_env(f"ansible-playbook '{playbook_path}'")


@task(
    depends_on_boolean=[Resource.JURY_HOST_UP, Resource.FORCAD_CONFIG_FILE_SAVED_TO_DISK],
    creates=[Resource.JURY_HOST_CONFIGURED],
)
def configure_jury(sync: Syncer):
    _run_playbook(ANSIBLE_JURY_CONF_PLAYBOOK_PATH).decode()
    sync.set_resource(Resource.JURY_HOST_CONFIGURED)


@task(
    depends_on_boolean=[Resource.JURY_HOST_CONFIGURED, Resource.ALL_VULNBOX_HOSTS_CONFIGURED],
    creates=[Resource.FORCAD_STARTED, Resource.TEAM_TOKENS],
)
def start_forcad(sync: Syncer):
    output = _run_playbook(ANSIBLE_JURY_RUN_PLAYBOOK_PATH).decode()

    team_tokens_match = re.search(r'"team_tokens\.stdout": "(?P<tokens>.*)"', output)
    if team_tokens_match is None:
        raise ValueError("Can't find team tokens in ForcAD output from Ansible")

    teams_to_tokens = team_tokens_match.group("tokens").split("\\n")
    team_tokens: TeamTokens = dict()
    for group in teams_to_tokens:
        team, token = group.rsplit(":", maxsplit=1)
        team_tokens[team] = token
        log(f'Received token "{token}" for team "{team}"')

    sync.set_resource(Resource.TEAM_TOKENS, team_tokens)
    sync.set_resource(Resource.FORCAD_STARTED)


@task(
    depends_on_boolean=[Resource.VPN_HOST_UP],
    creates=[Resource.VPN_HOST_CONFIGURED],
)
def configure_vpn(sync: Syncer):
    _run_playbook(ANSIBLE_VPN_CONF_PLAYBOOK_PATH)
    sync.set_resource(Resource.VPN_HOST_CONFIGURED)


@task(
    depends_on_boolean=[Resource.ALL_VULNBOX_HOSTS_UP],
    creates=[Resource.ALL_VULNBOX_HOSTS_CONFIGURED],
)
def configure_vulnboxes(sync: Syncer):
    _run_playbook(ANSIBLE_VULNBOXES_CONF_PLAYBOOK_PATH)
    sync.set_resource(Resource.ALL_VULNBOX_HOSTS_CONFIGURED)
