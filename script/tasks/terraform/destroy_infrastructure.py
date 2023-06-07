from models import Config
from tools import task, Syncer, Resource, process
from tasks.terraform.save_config import save_terraform_config
from constants.paths import TERRAFORM_PATH


@task(depends_on=[Resource.CONFIG])
def destroy_infrastructure(sync: Syncer, config: Config):
    save_terraform_config(config)
    process("terraform destroy -auto-approve", cwd=TERRAFORM_PATH)
    sync.set_resource(Resource.TERRAFORM_DESTROYED)
