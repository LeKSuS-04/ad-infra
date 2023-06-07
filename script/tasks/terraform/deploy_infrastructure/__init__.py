from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from constants.paths import TERRAFORM_PATH
from models import Config
from tools import task, Syncer, Resource, process
from tasks.terraform.prepare_config import save_terraform_config
from .output_parser import save_resources


@task(depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY])
def deploy_infrastructure(
    sync: Syncer, config: Config, ssh_key: EllipticCurvePrivateKey
):
    save_terraform_config(config, ssh_key)

    stdout = process("terraform apply -auto-approve", cwd=TERRAFORM_PATH)

    terraform_output = stdout.decode()
    save_resources(sync, terraform_output)
