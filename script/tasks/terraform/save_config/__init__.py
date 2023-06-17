from pathlib import Path
from typing import cast

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Config
from tools import Resource, Syncer, log, task
from tools.paths import TERRAFORM_CLOUD_INIT_CONFIG_PATH, TERRAFORM_CONFIG_PATH

_TEMPLATE_PATH = Path(__file__).parent
_JINJA_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_PATH),
    autoescape=cast(bool, select_autoescape()),
)


def _save_terraform_config(config: Config):
    with open(TERRAFORM_CONFIG_PATH, "w") as f:
        f.write(config.terraform_config.json())
        log(f"Saved terraform configuration into {TERRAFORM_CONFIG_PATH}")


def _save_cloud_init_config(ssh_key: EllipticCurvePrivateKey):
    with open(TERRAFORM_CLOUD_INIT_CONFIG_PATH, "w") as f:
        cloud_init_template = _JINJA_ENV.get_template("cloud-init.yaml.j2")
        public_key = (
            ssh_key.public_key()
            .public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)
            .decode()
        )
        rendered = cloud_init_template.render(public_key=public_key)
        f.write(cast(str, rendered))
        log(f"Saved cloud-init config into {TERRAFORM_CLOUD_INIT_CONFIG_PATH}")


@task(
    depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY],
    creates=[Resource.TERRAFORM_CONFIG_SAVED_TO_DISK],
)
def save_terraform_config(sync: Syncer, config: Config, ssh_key: EllipticCurvePrivateKey):
    _save_terraform_config(config)
    _save_cloud_init_config(ssh_key)
    sync.set_resource(Resource.TERRAFORM_CONFIG_SAVED_TO_DISK)
