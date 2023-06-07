import tarfile

from models import Config
from tools import task, Syncer, Resource
from constants.paths import GENERATED_PATH, INTERNAL_PATH, RESOURCES_PATH


@task(depends_on=[Resource.CONFIG])
def pack_sources(sync: Syncer, config: Config):
    base_path = RESOURCES_PATH / config.src_path
    services_tar = GENERATED_PATH / "services.tar.gz"
    sources_tar = INTERNAL_PATH / "checkers.tar.gz"

    for file in (services_tar, sources_tar):
        file.unlink(missing_ok=True)

    with tarfile.open(services_tar, "w") as tar:
        tar.add(base_path / "services", recursive=True)

    with tarfile.open(sources_tar, "w") as tar:
        tar.add(base_path / "checkers", recursive=True)

    sync.set_resource(Resource.SOURCES_PACKED)
