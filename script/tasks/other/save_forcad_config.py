import json

import yaml
from models import Config, ForcadConfig, VulnboxConfig
from tools import Resource, Syncer, task
from tools.paths import FORCAD_CONFIG_PATH


@task(
    depends_on=[Resource.CONFIG, Resource.VULNBOX_CONFIGS],
    creates=[Resource.FORCAD_CONFIG, Resource.FORCAD_CONFIG_FILE_SAVED_TO_DISK],
)
def save_forcad_config(sync: Syncer, config: Config, vulnbox_configs: dict[str, VulnboxConfig]):
    forcad_config = ForcadConfig.from_config(config, vulnbox_configs)
    sync.set_resource(Resource.FORCAD_CONFIG, forcad_config)

    jsonable_dict = json.loads(forcad_config.json(exclude_none=True))
    with open(FORCAD_CONFIG_PATH, "w") as f:
        yaml.dump(jsonable_dict, f, default_flow_style=False)
    sync.set_resource(Resource.FORCAD_CONFIG_FILE_SAVED_TO_DISK)
