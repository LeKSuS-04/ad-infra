from tools import Resource, Syncer, process, task
from tools.paths import TERRAFORM_DIR


@task(
    depends_on_boolean=[Resource.TERRAFORM_CONFIG_SAVED_TO_DISK],
    creates=[Resource.TERRAFORM_DESTROYED],
)
def destroy_infrastructure(sync: Syncer):
    process("terraform destroy -auto-approve", cwd=TERRAFORM_DIR)
    sync.set_resource(Resource.TERRAFORM_DESTROYED)
