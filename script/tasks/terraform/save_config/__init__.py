from pathlib import Path
from typing import cast

from constants.paths import TERRAFORM_PATH
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Config
from tools import Resource, Syncer, log, task

TEMPLATE_PATH = Path(__file__).parent
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH),
    autoescape=cast(bool, select_autoescape()),
)


def _save_terraform_config(config: Config):
    terraform_config_path = TERRAFORM_PATH / "variables.auto.tfvars.json"
    with open(terraform_config_path, "w") as f:
        f.write(config.terraform_config.json())
        log(f"Saved terraform configuration into {terraform_config_path}")


def _save_cloud_init_config(ssh_key: EllipticCurvePrivateKey):
    cloud_init_config_path = TERRAFORM_PATH / "cloud-init.yaml"
    with open(cloud_init_config_path, "w") as f:
        cloud_init_template = JINJA_ENV.get_template("cloud-init.yaml.j2")
        public_key = (
            ssh_key.public_key()
            .public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)
            .decode()
        )
        rendered = cloud_init_template.render(public_key=public_key)
        f.write(cast(str, rendered))
        log(f"Saved cloud-init config into {cloud_init_config_path}")


@task(depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY])
def save_terraform_config(sync: Syncer, config: Config, ssh_key: EllipticCurvePrivateKey):
    _save_terraform_config(config)
    _save_cloud_init_config(ssh_key)
    sync.set_resource(Resource.TERRAFORM_CONFIG_READY)
