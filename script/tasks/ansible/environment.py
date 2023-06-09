import os

from constants.paths import ANSIBLE_PATH
from tools import process


def run_with_ansible_env(command: str, **options) -> bytes:
    environment = dict()
    environment["ANSIBLE_CONFIG"] = str(ANSIBLE_PATH / "ansible.cfg")
    environment["ANSIBLE_LIBRARY"] = str(ANSIBLE_PATH / "library")

    if options.get("env") is not None:
        options["env"] |= environment
    else:
        options["env"] = os.environ.copy() | environment

    return process(command, **options)
