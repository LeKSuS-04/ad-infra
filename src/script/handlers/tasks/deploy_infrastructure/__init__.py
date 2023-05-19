from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from constants.paths import TERRAFORM_PATH
from models import Config
from utils.sync import Synchronizator, task
from utils.process import process
from utils.sync.resources import Resource
from .utils import save_cloud_init_config, save_terraform_config, save_resources


@task(depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY])
def deploy_infrastructure(sync: Synchronizator, config: Config, ssh_key: EllipticCurvePrivateKey):
    save_terraform_config(config)
    save_cloud_init_config(ssh_key)

    stdout = process('terraform apply -auto-approve', cwd=TERRAFORM_PATH)

    terraform_output = stdout.decode()
    save_resources(sync, terraform_output)
