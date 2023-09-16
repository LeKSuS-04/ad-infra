from tools import Resource, Syncer, process, task
from tools.paths import TERRAFORM_DIR

from .output_parser import save_resources


@task(
    depends_on_boolean=[Resource.TERRAFORM_CONFIG_SAVED_TO_DISK],
    creates=[
        Resource.VPN_HOST_PUBLIC_IP,
        Resource.JURY_HOST_PUBLIC_IP,
        Resource.VULNBOX_HOSTS_INTERNAL_IPS,
        Resource.BASTION_HOST_PUBLIC_IP,
        Resource.CONTAINER_REGISTRY_HOST_PUBLIC_IP,
        Resource.CONTAINER_REGISTRY_HOST_INTERNAL_IP,
    ],
)
def deploy_infrastructure(sync: Syncer):
    stdout = process("terraform apply -auto-approve", cwd=TERRAFORM_DIR)

    terraform_output = stdout.decode()
    save_resources(sync, terraform_output)
