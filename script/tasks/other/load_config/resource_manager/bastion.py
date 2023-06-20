from .abstract import VMResourceManager


class BastionResourceManager(VMResourceManager):
    @staticmethod
    def _guess_cores(**kwargs) -> int:
        return 2

    @staticmethod
    def _guess_ram(**kwargs) -> int:
        return 2

    @staticmethod
    def _guess_ssd(**kwargs) -> int:
        return 10
