import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from config.infra import VpnConfig
from netaddr import IPNetwork
from util.iterutil import skip_n
from util.log import get_logger

from .gen import generate_const_network, generate_group_network


def extract_vulnbox_address(file: Path) -> str:
    with file.open("r") as f:
        for line in f:
            if line.startswith("Address = "):
                return line.split(" = ")[1].strip()
    raise ValueError(f"Could not find vulnbox address in {file}")


@dataclass
class TeamVpnInfo:
    vulnbox_address: str
    team_subnet: str
    vpn_configs_path: Path
    vulnbox_filename: str


@dataclass
class VpnInfo:
    server_ports: list[int]
    server_config_paths: list[Path]
    vulnbox_subnet: str
    team_vpn_infos: list[TeamVpnInfo]
    jury_config_path: Path

    @property
    def server_interface_names(self) -> list[str]:
        def strip_ext(path: Path) -> str:
            return path.with_suffix("").name

        return [strip_ext(path) for path in self.server_config_paths]


class WireguardController:
    def __init__(
        self,
        server_address: str,
        infra_port: int,
        vulnbox_port: int,
        team_port: int,
        config: VpnConfig,
    ):
        self._server_address = server_address
        self._infra_port = infra_port
        self._vulnbox_port = vulnbox_port
        self._team_port = team_port

        self._bits_per_group = 8
        self._teams_subnet = IPNetwork("10.60.0.0/14")
        self._vulnbox_subnet = IPNetwork("10.80.0.0/14")
        self._jury_name = "jury"
        self._infra_subnets = {
            "jury": IPNetwork(f"{config.jury_ip}/32"),
        }
        if config.extra_services is not None:
            self._infra_subnets.update(
                {name: IPNetwork(f"{srv.ip}/32") for name, srv in config.extra_services.items()}
            )

        self._team_group_name = "team"
        self._vulnbox_group_name = "vuln"

        self._logger = get_logger("wireguard-controller")

    def generate_configs(  # noqa: C901
        self,
        total_teams: int,
        per_team: int,
        server_output_dir: Path,
        team_output_dir: Path,
        infra_output_dir: Path,
        jury_output_path: Path,
        get_team_dir_name: Callable[[int], str],
    ) -> VpnInfo:
        self._logger.info(f"Generating wireguard configs for {total_teams} teams")

        def exists_not_empty(path: Path) -> bool:
            if not path.exists():
                return False
            if not path.is_dir():
                return False
            return any(path.iterdir())

        team_nums = list(range(total_teams))
        if (
            exists_not_empty(server_output_dir)
            and exists_not_empty(infra_output_dir)
            and jury_output_path.exists()
            and all(exists_not_empty(team_output_dir / get_team_dir_name(i)) for i in team_nums)
        ):
            # TODO: right now this check is not strict enough.
            # It's better to ensure that discovered configs are EXACTLY the same as the ones
            # we would generate (in terms of quantity)
            # But it's not a big deal, so it remains like this for now.
            self._logger.info("Wireguard configs already exist, skipping generation")
            return self._discover_configs(
                total_teams=total_teams,
                server_output_dir=server_output_dir,
                team_output_dir=team_output_dir,
                get_team_dir_name=get_team_dir_name,
                jury_output_path=jury_output_path,
            )

        # Create directories if they don't exist
        server_output_dir.mkdir(parents=True, exist_ok=True)
        team_output_dir.mkdir(parents=True, exist_ok=True)
        infra_output_dir.mkdir(parents=True, exist_ok=True)

        tmp_path = Path(tempfile.gettempdir()) / "ad-infra-wireguard"

        tmp_teams_path = tmp_path / "team"
        tmp_vulnbox_path = tmp_path / "vuln"
        for path in [tmp_teams_path, tmp_vulnbox_path]:
            path.mkdir(parents=True, exist_ok=True)

        routed_subnets = [self._teams_subnet, self._vulnbox_subnet, *self._infra_subnets.values()]

        self._logger.info("Generating team configs")
        team_configs = generate_group_network(
            group_name=self._team_group_name,
            subnet=IPNetwork(self._teams_subnet),
            routed_subnets=routed_subnets,
            server_host=self._server_address,
            server_port=self._team_port,
            groups=team_nums,
            bits_per_group=self._bits_per_group,
            peers_per_group=per_team,
            peer_offset=0,
        )

        self._logger.info("Generating vulnbox configs")
        vulnbox_configs = generate_group_network(
            group_name=self._team_group_name,
            subnet=IPNetwork(self._teams_subnet),
            routed_subnets=routed_subnets,
            server_host=self._server_address,
            server_port=self._team_port,
            groups=team_nums,
            bits_per_group=self._bits_per_group,
            peers_per_group=1,
            peer_offset=1,
        )

        self._logger.info("Generating jury config")
        infra_configs = generate_const_network(
            server_host=self._server_address,
            server_port=self._infra_port,
            server_vpn_address=self._infra_subnets["jury"],
            peer_addresses={name: subnet for name, subnet in self._infra_subnets.items()},
            routed_subnets=routed_subnets,
        )

        self._logger.info("Dumping server configs")
        server_configs = {
            "team": team_configs.server_config,
            "vuln": vulnbox_configs.server_config,
            "infra": infra_configs.server_config,
        }
        server_config_paths = []
        server_interface_names = []
        for name, server_config in server_configs.items():
            config_path = server_output_dir / f"{name}.conf"
            config_path.write_text(server_config.dumps())
            server_config_paths.append(config_path)
            server_interface_names.append(name)

        self._logger.info("Dumping team configs")
        team_vpn_infos = []
        for team_num in team_nums:
            team_dir = team_output_dir / get_team_dir_name(team_num)
            team_dir.mkdir(parents=True, exist_ok=True)

            vulnbox_path = team_dir / f"{self._vulnbox_group_name}{team_num:03}.conf"
            vulnbox_path.write_text(vulnbox_configs.peer_configs[team_num].peers[0].dumps())

            for peer, conf in enumerate(team_configs.peer_configs[team_num].peers):
                config_path = team_dir / f"{self._team_group_name}{team_num:03}_{peer + 1}.conf"
                config_path.write_text(conf.dumps())

            team_vpn_infos.append(
                TeamVpnInfo(
                    team_subnet=str(team_configs.peer_configs[team_num].subnet),
                    vulnbox_address=extract_vulnbox_address(vulnbox_path),
                    vpn_configs_path=team_dir,
                    vulnbox_filename=vulnbox_path.name,
                )
            )

        self._logger.info("Dumping jury config")
        jury_path = jury_output_path
        jury_path.write_text(infra_configs.peer_configs[self._jury_name].dumps())

        self._logger.info("Dumping infra config")
        for name, config in infra_configs.peer_configs.items():
            if name == self._jury_name:
                continue

            infra_path = infra_output_dir / f"{name}.conf"
            infra_path.write_text(config.dumps())

        self._logger.info("Done")
        return VpnInfo(
            server_ports=[self._team_port, self._vulnbox_port, self._infra_port],
            server_config_paths=server_config_paths,
            vulnbox_subnet=str(self._vulnbox_subnet),
            team_vpn_infos=team_vpn_infos,
            jury_config_path=jury_path,
        )

    def _discover_configs(
        self,
        total_teams: int,
        server_output_dir: Path,
        team_output_dir: Path,
        jury_output_path: Path,
        get_team_dir_name: Callable[[int], str],
    ) -> VpnInfo:
        server_configs = list(server_output_dir.glob("*.conf"))
        team_configs = []
        for team_subnet, team_dir in zip(
            skip_n(self._teams_subnet.subnet(32 - self._bits_per_group), 1),
            map(team_output_dir.joinpath, map(get_team_dir_name, range(total_teams))),
        ):
            if team_dir.is_dir():
                vulnbox_filename = list(team_dir.glob(f"{self._vulnbox_group_name}*.conf"))
                msg = f"Expected exactly one vulnbox filename, got {len(vulnbox_filename)}"
                assert len(vulnbox_filename) == 1, msg
                vulnbox_filename = vulnbox_filename[0].name

                team_configs.append(
                    TeamVpnInfo(
                        vpn_configs_path=team_dir,
                        team_subnet=str(team_subnet),
                        vulnbox_filename=vulnbox_filename,
                        vulnbox_address=extract_vulnbox_address(team_dir / vulnbox_filename),
                    )
                )

        return VpnInfo(
            server_ports=[self._team_port, self._vulnbox_port, self._infra_port],
            server_config_paths=server_configs,
            vulnbox_subnet=str(self._vulnbox_subnet),
            team_vpn_infos=team_configs,
            jury_config_path=jury_output_path,
        )
