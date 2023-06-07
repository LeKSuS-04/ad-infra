from models import Config
from tools import task, Syncer, Resource, process
from tasks.terraform.prepare_config import save_terraform_config
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from constants.paths import TERRAFORM_PATH


@task(depends_on=[Resource.CONFIG, Resource.ADMIN_SSH_KEY])
def destroy_infrastructure(
    sync: Syncer, config: Config, ssh_key: EllipticCurvePrivateKey
):
    save_terraform_config(config, ssh_key)
    process("terraform destroy -auto-approve", cwd=TERRAFORM_PATH)
    sync.set_resource(Resource.TERRAFORM_DESTROYED)
