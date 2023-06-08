from constants.paths import TERRAFORM_PATH
from tools import Resource, Syncer, process, task

from .output_parser import save_resources


@task(depends_on=[Resource.TERRAFORM_CONFIG_READY])
def deploy_infrastructure(sync: Syncer, terraform_config_ready: bool):
    stdout = process("terraform apply -auto-approve", cwd=TERRAFORM_PATH)

    terraform_output = stdout.decode()
    save_resources(sync, terraform_output)
