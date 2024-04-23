from ipaddress import IPv4Address
from pathlib import PosixPath

import yaml
from models import Config, ForcadConfig, VulnboxConfig
from tools import Resource, Syncer, task
from tools.paths import FORCAD_CONFIG_PATH


def posix_path_representer(d: yaml.SafeDumper, path: PosixPath) -> yaml.nodes.ScalarNode:
    return d.represent_str(str(path))


def ipv4_address_representer(d: yaml.SafeDumper, address: IPv4Address) -> yaml.nodes.ScalarNode:
    return d.represent_str(str(address))


def get_dumper():
    safe_dumper = yaml.SafeDumper
    safe_dumper.add_representer(PosixPath, posix_path_representer)
    safe_dumper.add_representer(IPv4Address, ipv4_address_representer)
    return safe_dumper


@task(
    depends_on=[Resource.CONFIG, Resource.VULNBOX_CONFIGS],
    creates=[Resource.FORCAD_CONFIG, Resource.FORCAD_CONFIG_FILE_SAVED_TO_DISK],
)
def save_forcad_config(sync: Syncer, config: Config, vulnbox_configs: dict[str, VulnboxConfig]):
    forcad_config = ForcadConfig.from_config(config, vulnbox_configs)
    sync.set_resource(Resource.FORCAD_CONFIG, forcad_config)

    with open(FORCAD_CONFIG_PATH, "w") as f:
        yaml.dump(forcad_config.dict(), f, Dumper=get_dumper())
    sync.set_resource(Resource.FORCAD_CONFIG_FILE_SAVED_TO_DISK)
