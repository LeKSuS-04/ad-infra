from models import ResourceEstimationBehaviour, Team

from .abstract import VMResourceManager


class VPNResourceManager(VMResourceManager):
    @staticmethod
    def _guess_cores(behaviour: ResourceEstimationBehaviour, teams: list[Team], **kwargs) -> int:
        match behaviour:
            case ResourceEstimationBehaviour.LOW:
                cores = len(teams) / 40

            case ResourceEstimationBehaviour.MEDIUM:
                cores = len(teams) / 20

            case ResourceEstimationBehaviour.BIG:
                cores = len(teams) / 10

        return VMResourceManager._ceil_to_multiple_of_two(cores)

    @staticmethod
    def _guess_ram(**kwargs) -> int:
        return VPNResourceManager._guess_cores(**kwargs)

    @staticmethod
    def _guess_ssd(**kwargs) -> int:
        return 10
