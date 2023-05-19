import tarfile
from pathlib import Path

from models import Config
from utils.sync import task, Synchronizator
from utils.sync.resources import Resource
from constants.paths import GENERATED_PATH, TEMPORARY_PATH


@task(depends_on=[Resource.CONFIG])
def pack_sources(sync: Synchronizator, config: Config):
    base_path = Path(config.src_path)

    with tarfile.open(GENERATED_PATH / 'services.tar.gz', 'w') as tar:
        tar.add(base_path / 'services', recursive=True)

    with tarfile.open(TEMPORARY_PATH / 'checkers.tar.gz', 'w') as tar:
        tar.add(base_path / 'checkers', recursive=True)

    sync.set_resource(Resource.SOURCES_PACKED)
