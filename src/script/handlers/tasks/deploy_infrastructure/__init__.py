from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from models import Config
from synchronization import Synchronizator, task
from synchronization.resources import Resource
from utils.process import process
from .utils import save_cloud_init_config, save_terraform_config, save_resources, TERRAFORM_DIR_PATH


@task(depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY])
def deploy_infrastructure(sync: Synchronizator, config: Config, ssh_key: EllipticCurvePrivateKey):
    save_terraform_config(config)
    save_cloud_init_config(ssh_key)

    stdout = process('terraform apply -auto-approve', cwd=TERRAFORM_DIR_PATH)

    terraform_output = stdout.decode()
    save_resources(sync, terraform_output)
