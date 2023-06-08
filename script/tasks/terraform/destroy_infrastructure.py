from tools import task, Syncer, Resource, process
from constants.paths import TERRAFORM_PATH


@task(depends_on=[Resource.TERRAFORM_CONFIG_READY])
def destroy_infrastructure(sync: Syncer, terraform_config_ready: bool):
    process("terraform destroy -auto-approve", cwd=TERRAFORM_PATH)
    sync.set_resource(Resource.TERRAFORM_DESTROYED)
