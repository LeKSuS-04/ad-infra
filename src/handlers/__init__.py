from typing import Callable

from .deploy import deploy


def get_handler(name: str) -> Callable[[], None]:
    if name == 'deploy':
        return deploy

    raise ValueError('Unknown handler name')
