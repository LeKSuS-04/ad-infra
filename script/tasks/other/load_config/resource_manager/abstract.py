from abc import ABCMeta, abstractstaticmethod
from math import ceil
from typing import Protocol

from models import (
    LoadedConfig,
    LoadedTeam,
    ResourceEstimationBehaviour,
    VMConfig,
    VMResources,
)


class GuesserFunction(Protocol):
    def __call__(
        self,
        behaviour: int | ResourceEstimationBehaviour,
        config: LoadedConfig,
        teams: list[LoadedTeam],
    ) -> int:
        ...


class VMResourceManager(metaclass=ABCMeta):
    _cores_config: int | ResourceEstimationBehaviour
    _ram_config: int | ResourceEstimationBehaviour
    _ssd_config: int | ResourceEstimationBehaviour

    def __init__(
        self,
        resources: VMResources | ResourceEstimationBehaviour,
    ):
        if isinstance(resources, VMResources):
            self._cores_config = resources.cores
            self._ram_config = resources.ram_gb
            self._ssd_config = resources.ssd_gb
        else:
            self._cores_config = resources
            self._ram_config = resources
            self._ssd_config = resources

    def value_or_guess(
        self,
        value: int | ResourceEstimationBehaviour,
        guesser: GuesserFunction,
        config: LoadedConfig,
        teams: list[LoadedTeam],
    ) -> int:
        if isinstance(value, int):
            return value
        return guesser(
            behaviour=value,
            config=config,
            teams=teams,
        )

    @staticmethod
    def ceil_to_multiple_of_two(value: int | float) -> int:
        return ceil(value / 2) * 2

    def _cores(self, **config_kwargs) -> int:
        return self.value_or_guess(self._cores_config, self._guess_cores, **config_kwargs)

    def _ram_gb(self, **config_kwargs) -> int:
        return self.value_or_guess(self._ram_config, self._guess_ram, **config_kwargs)

    def _ssd_gb(self, **config_kwargs) -> int:
        return self.value_or_guess(self._ssd_config, self._guess_ssd, **config_kwargs)

    @abstractstaticmethod
    def _guess_cores(
        behaviour: int | ResourceEstimationBehaviour,  # type: ignore # noqa: N805
        config: LoadedConfig,
        teams: list[LoadedTeam],
    ) -> int:
        ...

    @abstractstaticmethod
    def _guess_ram(
        behaviour: int | ResourceEstimationBehaviour,  # type: ignore # noqa: N805
        config: LoadedConfig,
        teams: list[LoadedTeam],
    ) -> int:  # type: ignore
        ...

    @abstractstaticmethod
    def _guess_ssd(
        behaviour: int | ResourceEstimationBehaviour,  # type: ignore # noqa: N805
        config: LoadedConfig,
        teams: list[LoadedTeam],
    ) -> int:  # type: ignore
        ...

    def get_config(self, config: LoadedConfig, teams: list[LoadedTeam]) -> VMConfig:
        config_kwargs = {'config': config, 'teams': teams}
        return VMConfig(
            cores=self._cores(**config_kwargs),
            ram_gb=self._ram_gb(**config_kwargs),
            ssd_gb=self._ssd_gb(**config_kwargs),
        )
