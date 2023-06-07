from constants.paths import TERRAFORM_PATH
from models import Config
from tools import log


def save_terraform_config(config: Config):
    terraform_config_path = TERRAFORM_PATH / "variables.auto.tfvars.json"
    with open(terraform_config_path, "w") as f:
        f.write(config.terraform_config.json())
        log(f"Saved terraform configuration into {terraform_config_path}")
