from math import ceil

from models import LoadedConfig, LoadedTeam, ResourceEstimationBehaviour

from .abstract import VMResourceManager


class VulnboxResourceManager(VMResourceManager):
    @staticmethod
    def _guess_cores(
        behaviour: ResourceEstimationBehaviour, config: LoadedConfig, teams: list[LoadedTeam]
    ) -> int:
        match behaviour:
            case ResourceEstimationBehaviour.LOW:
                cores = len(config.tasks) / 4

            case ResourceEstimationBehaviour.MEDIUM:
                cores = 2 + len(config.tasks) / 2

            case ResourceEstimationBehaviour.BIG:
                cores = 4 + len(config.tasks)

        return VMResourceManager._ceil_to_multiple_of_two(cores)

    @staticmethod
    def _guess_ram(**kwargs) -> int:
        return VulnboxResourceManager._guess_cores(**kwargs)

    @staticmethod
    def _guess_ssd(
        behaviour: ResourceEstimationBehaviour, config: LoadedConfig, teams: list[LoadedTeam]
    ) -> int:
        match behaviour:
            case ResourceEstimationBehaviour.LOW:
                ssd_gb = 5 + len(config.tasks) * 0.25

            case ResourceEstimationBehaviour.MEDIUM:
                ssd_gb = 10 + len(config.tasks) * 0.5

            case ResourceEstimationBehaviour.BIG:
                ssd_gb = 15 + len(config.tasks)

        return ceil(ssd_gb)
