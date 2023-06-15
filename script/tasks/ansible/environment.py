import os

from constants.paths import ANSIBLE_CONFIG_PATH, ANSIBLE_INVENTORY_PATH, ANSIBLE_LIBRARY_DIR
from tools import process


def run_with_ansible_env(command: str, **options) -> bytes:
    environment = dict()
    environment["ANSIBLE_CONFIG"] = ANSIBLE_CONFIG_PATH
    environment["ANSIBLE_LIBRARY"] = ANSIBLE_LIBRARY_DIR
    environment["ANSIBLE_INVENTORY"] = ANSIBLE_INVENTORY_PATH

    if options.get("env") is not None:
        options["env"] |= environment
    else:
        options["env"] = os.environ.copy() | environment

    return process(command, **options)
