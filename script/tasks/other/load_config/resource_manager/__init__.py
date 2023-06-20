from models import (
    LoadedConfig,
    LoadedTeam,
    ResourceEstimationBehaviour,
    ResourcesPerVMConfig,
    VMConfig,
    VMResources,
)

from .bastion import BastionResourceManager
from .jury import JuryResourceManager
from .vpn import VPNResourceManager
from .vulnbox import VulnboxResourceManager


class ResourceManager:
    _jury_config: VMResources | ResourceEstimationBehaviour
    _vpn_config: VMResources | ResourceEstimationBehaviour
    _vulnbox_config: VMResources | ResourceEstimationBehaviour
    _bastion_config: VMResources | ResourceEstimationBehaviour

    def __init__(self, resource_config: ResourcesPerVMConfig | ResourceEstimationBehaviour):
        if isinstance(resource_config, ResourcesPerVMConfig):
            self._jury_config = resource_config.jury
            self._vpn_config = resource_config.vpn
            self._vulnbox_config = resource_config.vulnbox
            self._bastion_config = resource_config.bastion
        else:
            self._jury_config = (
                self._vpn_config
            ) = self._vulnbox_config = self._bastion_config = resource_config

    def get_jury_resources(self, config: LoadedConfig, teams: list[LoadedTeam]) -> VMConfig:
        guesser = JuryResourceManager(self._jury_config)
        return guesser.get_config(config, teams)

    def get_vpn_resources(self, config: LoadedConfig, teams: list[LoadedTeam]) -> VMConfig:
        guesser = VPNResourceManager(self._vpn_config)
        return guesser.get_config(config, teams)

    def get_vulnbox_resources(self, config: LoadedConfig, teams: list[LoadedTeam]) -> VMConfig:
        guesser = VulnboxResourceManager(self._vulnbox_config)
        return guesser.get_config(config, teams)

    def get_bastion_resources(self, config: LoadedConfig, teams: list[LoadedTeam]) -> VMConfig:
        guesser = BastionResourceManager(self._bastion_config)
        return guesser.get_config(config, teams)
