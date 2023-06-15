from constants.paths import TERRAFORM_DIR
from tools import Resource, Syncer, process, task

from .output_parser import save_resources


@task(depends_on_boolean=[Resource.TERRAFORM_CONFIG_READY])
def deploy_infrastructure(sync: Syncer):
    stdout = process("terraform apply -auto-approve", cwd=TERRAFORM_DIR)

    terraform_output = stdout.decode()
    save_resources(sync, terraform_output)
