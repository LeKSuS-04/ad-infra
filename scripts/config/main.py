import json
import yaml
from jsonschema import validate
from pathlib import Path
from typing import Any
from schemas import CONFIG_SCHEMA, TEAMS_CONFIG_SCHEMA


def make_archiver_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        'services': config['sources']['services'],
        'checkers': config['sources']['checkers'],
    }


def make_terraform_config(
    config: dict[str, Any], teams: dict[str, Any]
) -> dict[str, Any]:
    return {
        'yandex_cloud_folder_id': config['yandex-cloud']['folder-id'],
        'yandex_cloud_zone': config['yandex-cloud']['zone'],
        'yandex_cloud_iam_token': config['yandex-cloud']['iam-token'],
    }


if __name__ == '__main__':
    with open('config.yaml', 'r') as config_file, open('teams.yaml', 'r') as teams_file:
        config = yaml.load(config_file, yaml.SafeLoader)
        teams = yaml.load(teams_file, yaml.SafeLoader)
        validate(config, CONFIG_SCHEMA)
        validate(teams, TEAMS_CONFIG_SCHEMA)

    terraform_dir = Path.cwd() / 'terraform'
    config_dir = Path.cwd() / 'resources' / 'configs'
    config_dir.mkdir(exist_ok=True)

    with open(f'{config_dir}/archiver.json', 'w') as f:
        json.dump(make_archiver_config(config), f)

    with open(f'{terraform_dir}/terraform.auto.tfvars.json', 'w') as f:
        json.dump(make_terraform_config(config, teams), f)
