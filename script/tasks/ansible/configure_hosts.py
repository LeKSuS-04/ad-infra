import re

from models import TeamTokens
from tools import Resource, Syncer, log, task
from tools.paths import (
    ANSIBLE_CONTAINER_REGISTRY_CONF_PLAYBOOK_PATH,
    ANSIBLE_JURY_CONF_PLAYBOOK_PATH,
    ANSIBLE_JURY_RUN_PLAYBOOK_PATH,
    ANSIBLE_VPN_CONF_PLAYBOOK_PATH,
    ANSIBLE_VULNBOXES_CONF_PLAYBOOK_PATH,
)

from .environment import run_playbook


@task(
    depends_on_boolean=[Resource.CONTAINER_REGISTRY_HOST_UP, Resource.DOCKER_CONFIG_SAVED_TO_DISK],
    creates=[Resource.CONTAINER_REGISTRY_HOST_CONFIGURED],
)
def configure_container_registry(sync: Syncer):
    run_playbook(ANSIBLE_CONTAINER_REGISTRY_CONF_PLAYBOOK_PATH, max_retries=2).decode()
    sync.set_resource(Resource.CONTAINER_REGISTRY_HOST_CONFIGURED)


@task(
    depends_on_boolean=[
        Resource.JURY_HOST_UP,
        Resource.FORCAD_CONFIG_FILE_SAVED_TO_DISK,
        Resource.CONTAINER_REGISTRY_HOST_CONFIGURED,
    ],
    creates=[Resource.JURY_HOST_CONFIGURED],
)
def configure_jury(sync: Syncer):
    run_playbook(ANSIBLE_JURY_CONF_PLAYBOOK_PATH, max_retries=2).decode()
    sync.set_resource(Resource.JURY_HOST_CONFIGURED)


@task(
    depends_on_boolean=[
        Resource.JURY_HOST_CONFIGURED,
        Resource.ALL_VULNBOX_HOSTS_CONFIGURED,
        Resource.VPN_HOST_CONFIGURED,
    ],
    creates=[Resource.FORCAD_STARTED, Resource.TEAM_TOKENS],
)
def start_forcad(sync: Syncer):
    output = run_playbook(ANSIBLE_JURY_RUN_PLAYBOOK_PATH, max_retries=2).decode()

    team_tokens_match = re.search(r'"team_tokens\.stdout": "(?P<tokens>.*)"', output)
    if team_tokens_match is None:
        raise ValueError("Can't find team tokens in ForcAD output from Ansible")

    teams_to_tokens = team_tokens_match.group("tokens").split("\\n")
    team_tokens: TeamTokens = dict()
    for group in teams_to_tokens:
        team, token = group.rsplit(":", maxsplit=1)
        team = team.replace('\\"', '"')
        team_tokens[team] = token
        log(f'Received token "{token}" for team "{team}"')

    sync.set_resource(Resource.TEAM_TOKENS, team_tokens)
    sync.set_resource(Resource.FORCAD_STARTED)


@task(
    depends_on_boolean=[Resource.VPN_HOST_UP],
    creates=[Resource.VPN_HOST_CONFIGURED],
)
def configure_vpn(sync: Syncer):
    run_playbook(ANSIBLE_VPN_CONF_PLAYBOOK_PATH, max_retries=3)
    sync.set_resource(Resource.VPN_HOST_CONFIGURED)


@task(
    depends_on_boolean=[Resource.ALL_VULNBOX_HOSTS_UP, Resource.CONTAINER_REGISTRY_HOST_CONFIGURED],
    creates=[Resource.ALL_VULNBOX_HOSTS_CONFIGURED],
)
def configure_vulnboxes(sync: Syncer):
    run_playbook(ANSIBLE_VULNBOXES_CONF_PLAYBOOK_PATH, max_retries=10)
    sync.set_resource(Resource.ALL_VULNBOX_HOSTS_CONFIGURED)
