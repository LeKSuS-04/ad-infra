import json

import yaml
from constants.paths import GENERATED_PATH
from models import Config, ForcadConfig
from tools import Resource, Syncer, task


@task(depends_on=[Resource.CONFIG])
def save_forcad_config(sync: Syncer, config: Config):
    with open(GENERATED_PATH / "forcad.yaml", "w") as f:
        forcad_config = ForcadConfig.from_config(config)
        jsonable_dict = json.loads(forcad_config.json(exclude_none=True))
        yaml.dump(jsonable_dict, f, default_flow_style=False)
    sync.set_resource(Resource.FORCAD_CONFIG_READY)
