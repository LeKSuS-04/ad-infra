import os
import shutil
from pathlib import Path

from constants.paths import (
    ANSIBLE_INVENTORY_PATH,
    PRIVATE_GENERATED_DIR,
    PUBLIC_GENERATED_DIR,
    TERRAFORM_CLOUD_INIT_CONFIG_PATH,
    TERRAFORM_CONFIG_PATH,
)
from tools import Resource, Syncer, log, task


def clean_directory(dir_path: Path):
    try:
        with os.scandir(dir_path) as it:
            for entity in it:
                if entity.is_dir():
                    shutil.rmtree(entity)
                else:
                    if entity.name != ".keep":
                        os.remove(entity)
        log(f'Cleaned "{dir_path.name}"')
    except FileNotFoundError:
        log(f"Didn't clean \"{dir_path.name}\" because it doesn't exist")


def verbose_remove(file_path: Path):
    try:
        os.remove(file_path)
        log(f'Removed "{file_path.name}"')
    except FileNotFoundError:
        log(f"Didn't remove \"{file_path.name}\" because it doesn't exist")


@task(depends_on_boolean=[Resource.TERRAFORM_DESTROYED])
def clean_filesystem(sync: Syncer):
    clean_directory(PUBLIC_GENERATED_DIR)
    clean_directory(PRIVATE_GENERATED_DIR)

    verbose_remove(ANSIBLE_INVENTORY_PATH)

    verbose_remove(TERRAFORM_CONFIG_PATH)
    verbose_remove(TERRAFORM_CLOUD_INIT_CONFIG_PATH)

    sync.set_resource(Resource.FILESYSTEM_CLEANED)
