from math import ceil

from models import LoadedConfig, LoadedTeam, ResourceEstimationBehaviour

from .abstract import VMResourceManager


class JuryResourceManager(VMResourceManager):
    @staticmethod
    def _guess_cores(
        behaviour: ResourceEstimationBehaviour, config: LoadedConfig, teams: list[LoadedTeam]
    ) -> int:
        match behaviour:
            case ResourceEstimationBehaviour.LOW:
                cores = len(teams) * len(config.tasks) / 40

            case ResourceEstimationBehaviour.MEDIUM:
                cores = 2 + len(teams) * len(config.tasks) / 20

            case ResourceEstimationBehaviour.BIG:
                cores = 4 + len(teams) * len(config.tasks) / 15

        return VMResourceManager.ceil_to_multiple_of_two(cores)

    @staticmethod
    def _guess_ram(**kwargs) -> int:
        return JuryResourceManager._guess_cores(**kwargs)

    @staticmethod
    def _guess_ssd(
        behaviour: ResourceEstimationBehaviour, config: LoadedConfig, teams: list[LoadedTeam]
    ) -> int:
        match behaviour:
            case ResourceEstimationBehaviour.LOW:
                ssd_gb = 8 + len(config.tasks) * 0.1

            case ResourceEstimationBehaviour.MEDIUM:
                ssd_gb = 12 + len(config.tasks) * 0.25

            case ResourceEstimationBehaviour.BIG:
                ssd_gb = 15 + len(config.tasks) * 0.5

        return ceil(ssd_gb)
