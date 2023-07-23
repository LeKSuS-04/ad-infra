from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader, select_autoescape
from tools import Resource, Syncer, task
from tools.paths import DOCKER_DAEMON_CONFIG_PATH

_TEMPLATE_PATH = Path(__file__).parent
_JINJA_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_PATH), autoescape=cast(bool, select_autoescape())
)


@task(
    depends_on=[Resource.CONTAINER_REGISTRY_HOST_INTERNAL_IP],
    creates=[Resource.DOCKER_CONFIG_SAVED_TO_DISK],
)
def prepare_docker_config(sync: Syncer, container_registry_host: str):
    template_params = dict(mirror_ip=container_registry_host)

    with open(DOCKER_DAEMON_CONFIG_PATH, "w") as f:
        inventory_template = _JINJA_ENV.get_template("daemon.json.j2")
        rendered = inventory_template.render(**template_params)
        f.write(cast(str, rendered))

    sync.set_resource(Resource.DOCKER_CONFIG_SAVED_TO_DISK)
