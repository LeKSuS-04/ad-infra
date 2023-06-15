from constants.paths import TERRAFORM_DIR
from tools import Resource, Syncer, process, task


@task(depends_on_boolean=[Resource.TERRAFORM_CONFIG_READY])
def destroy_infrastructure(sync: Syncer):
    process("terraform destroy -auto-approve", cwd=TERRAFORM_DIR)
    sync.set_resource(Resource.TERRAFORM_DESTROYED)
