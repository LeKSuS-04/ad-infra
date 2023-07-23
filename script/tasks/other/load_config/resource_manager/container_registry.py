from math import ceil

from models import LoadedConfig, ResourceEstimationBehaviour

from .abstract import VMResourceManager


class ContainerRegistryResourceManager(VMResourceManager):
    @staticmethod
    def _guess_cores(**kwargs) -> int:
        return 2

    @staticmethod
    def _guess_ram(**kwargs) -> int:
        return 2

    @staticmethod
    def _guess_ssd(behaviour: ResourceEstimationBehaviour, config: LoadedConfig, **kwargs) -> int:
        match behaviour:
            case ResourceEstimationBehaviour.LOW:
                ssd_gb = 8 + len(config.tasks) * 0.5

            case ResourceEstimationBehaviour.MEDIUM:
                ssd_gb = 12 + len(config.tasks) * 1

            case ResourceEstimationBehaviour.BIG:
                ssd_gb = 15 + len(config.tasks) * 2

        return ceil(ssd_gb)
