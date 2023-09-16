import os
from pathlib import Path
from typing import Any

from tools import process
from tools.paths import (
    ANSIBLE_CONFIG_PATH,
    ANSIBLE_INVENTORY_PATH,
    ANSIBLE_RETRY_FILES_DIR,
)


def _add_to_env(options: dict[str, Any], key: str, value: Any):
    if options.get("env") is None:
        options["env"] = os.environ.copy()
    options["env"][key] = value


def _remove_extension(filename: str) -> str:
    return ".".join(filename.split(".")[:-1])


def _add_limit_flag(command: str, playbook: Path) -> str:
    playbook_name = _remove_extension(playbook.name)
    retry_file = ANSIBLE_RETRY_FILES_DIR / f"{playbook_name}.retry"

    if not retry_file.exists:
        raise FileNotFoundError(f"Retry file {retry_file} does not exist")

    limit_flag = f"--limit @{retry_file}"
    if limit_flag in command:
        return command
    else:
        return f"{command} {limit_flag}"


def run_with_ansible_env(command: str, **options) -> bytes:
    _add_to_env(options, "ANSIBLE_CONFIG", ANSIBLE_CONFIG_PATH)
    _add_to_env(options, "ANSIBLE_INVENTORY", ANSIBLE_INVENTORY_PATH)
    _add_to_env(options, "ANSIBLE_RETRY_FILES_ENABLED", "True")
    _add_to_env(options, "ANSIBLE_RETRY_FILES_SAVE_PATH", ANSIBLE_RETRY_FILES_DIR)
    return process(command, **options)


def run_playbook(playbook: Path, max_retries: int = 1, **options) -> bytes:
    has_succeeded = False
    output = b""
    retries = 0
    exception = None

    command = f"ansible-playbook {playbook}"

    while not has_succeeded and retries < max_retries:
        try:
            output = run_with_ansible_env(command, **options)
            has_succeeded = True
        except ValueError as ex:
            exception = ex
            command = _add_limit_flag(command, playbook)
            retries += 1

            print(f"Failed to run playbook {playbook}: some hosts did not succeed")
            print(f"{max_retries - retries} retries left")

    if not has_succeeded and exception is not None:
        raise exception

    return output
