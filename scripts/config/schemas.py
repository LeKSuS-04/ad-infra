CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'yandex-cloud': {
            'type': 'object',
            'properties': {
                'folder-id': {'type': 'string'},
                'zone': {
                    'enum': [
                        'ru-central1-a',
                        'ru-central1-b',
                        'ru-central1-c',
                    ]
                },
                'iam-token': {'type': 'string'},
            },
            'required': ['folder-id', 'zone', 'iam-token'],
            'additionalProperties': False,
        },
        'sources': {
            'type': 'object',
            'properties': {
                'services': {'type': 'string'},
                'checkers': {'type': 'string'},
            },
            'required': ['services', 'checkers'],
            'additionalProperties': False,
        },
        'teams': {
            'type': 'object',
            'properties': {
                'players-per-team': {'type': 'integer', 'minimum': 0},
            },
            'required': ['players-per-team'],
            'additionalProperties': False,
        },
    },
    'required': ['yandex-cloud', 'sources', 'teams'],
    'additionalProperties': False,
}

TEAMS_CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'teams': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
                'required': ['name'],
                'additionalProperties': False,
            },
            'minItems': 1,
        }
    },
    'required': ['teams'],
    'additionalProperties': False,
}
