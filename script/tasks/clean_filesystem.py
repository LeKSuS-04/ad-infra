import os
import shutil
from pathlib import Path

from constants.paths import ANSIBLE_PATH, GENERATED_PATH, INTERNAL_PATH, TERRAFORM_PATH
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


@task(depends_on=[Resource.TERRAFORM_DESTROYED])
def clean_filesystem(sync: Syncer, terraform_testroyed: bool):
    clean_directory(GENERATED_PATH)
    clean_directory(INTERNAL_PATH)

    ansible_inventory = ANSIBLE_PATH / "inventory.yaml"
    verbose_remove(ansible_inventory)

    cloud_init_config = TERRAFORM_PATH / "cloud-init.yaml"
    verbose_remove(cloud_init_config)

    sync.set_resource(Resource.FILESYSTEM_CLEANED)
