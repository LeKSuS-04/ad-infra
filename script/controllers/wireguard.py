import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from netaddr import IPNetwork
from util.log import get_logger


class WGKey:
    def __init__(self, public: str, private: str):
        self.public = public
        self.private = private

    @classmethod
    def generate(cls):
        private_key = cls._generate_private_key()
        public_key = cls._public_from_private(private_key)
        return cls(public=public_key, private=private_key)

    @staticmethod
    def _generate_private_key() -> str:
        return subprocess.check_output(["wg", "genkey"]).decode().strip()

    @staticmethod
    def _public_from_private(private: str) -> str:
        inp = private.encode()
        data = subprocess.check_output(["wg", "pubkey"], input=inp).decode().strip()
        return data


class ConfigSection:
    def __init__(self, name: str, values: dict[str, Any], comment: str | None = None):
        self.name = name
        self.values = values
        self.comment = comment

    def dumps(self):
        headers = f"[{self.name}]\n"
        comment = f"# {self.comment}\n" if self.comment else ""
        content = "\n".join(f"{k} = {v}" for k, v in self.values.items())
        return headers + comment + content


class WGConfig:
    def __init__(self):
        self.sections = []
        self.others = {}

    def add_section(self, section: ConfigSection):
        self.sections.append(section)

    def add_value(self, key: str, value: Any):
        self.others[key] = value

    def dumps(self):
        sections = "\n\n".join(s.dumps() for s in self.sections)
        values = "\n".join(f"{k} = {v}" for k, v in self.others.items())
        return sections + "\n\n" + values + "\n"


class WGGenerator:
    def __init__(
        self,
        server: str,
        server_port: int,
        server_number: int,
        per_group: int,
        group_list: list[int],
        single_peer: bool,
        subnet: str,
        subnet_newbits: int,
        routed_subnets: str,
        group_name: str,
    ):
        self._server_host = server
        self._server_port = server_port
        self._server_number = server_number
        self._per_group = per_group
        self._group_list = group_list
        self._single_peer = single_peer
        self._subnet = IPNetwork(subnet)
        self._subnet_newbits = subnet_newbits
        self._routed_subnets = routed_subnets
        self._group_name = group_name

        need_bits = self._subnet.prefixlen + self._subnet_newbits
        self._group_subnets = list(self._subnet.subnet(need_bits))

        self._server_key = WGKey.generate()
        self._peer_keys: dict[int, dict[int, WGKey]] = {}

        self.server_config = None
        self._peers_in_group = 1 if self._single_peer else self._per_group
        self.peer_configs: dict[int, dict[int, WGConfig]] = {}

        self._generate_peer_keys()
        self._generate_configs()

    def _generate_peer_keys(self):
        for group in self._group_list:
            self._peer_keys[group] = {}
            for peer in range(self._peers_in_group):
                self._peer_keys[group][peer] = WGKey.generate()

    def _generate_configs(self):
        self.server_config = WGConfig()

        interface_section = ConfigSection(
            name="Interface",
            values={
                "Address": str(self._subnet[1]),
                "PrivateKey": self._server_key.private,
                "ListenPort": self._server_port,
            },
        )
        self.server_config.add_section(interface_section)

        for group in self._group_list:
            cur_net = self._group_subnets[group]
            self.peer_configs[group] = {}

            for peer in range(self._peers_in_group):
                peer_subnet = list(cur_net.subnet(32))[2 + peer]
                peer_section = ConfigSection(
                    name="Peer",
                    values={
                        "PublicKey": self._peer_keys[group][peer].public,
                        "AllowedIPs": str(peer_subnet),
                    },
                    comment=f"friendly_name = {self._group_name}{group}",
                )
                self.server_config.add_section(peer_section)

                peer_conf = WGConfig()

                peer_interface = ConfigSection(
                    name="Interface",
                    values={
                        "Address": str(peer_subnet[0]),
                        "PrivateKey": self._peer_keys[group][peer].private,
                        "ListenPort": 21000
                        + (self._server_number % 1000) * 1000
                        + group * self._per_group
                        + peer,
                    },
                )
                peer_conf.add_section(peer_interface)

                endpoint_section = ConfigSection(
                    name="Peer",
                    values={
                        "PublicKey": self._server_key.public,
                        "Endpoint": f"{self._server_host}:{self._server_port}",
                        "AllowedIPs": self._routed_subnets,
                    },
                )
                peer_conf.add_section(endpoint_section)
                peer_conf.add_value("PersistentKeepalive", 25)

                self.peer_configs[group][peer] = peer_conf


def extract_vulnbox_address(file: Path) -> str:
    with file.open("r") as f:
        for line in f:
            if line.startswith("Address = "):
                return line.split(" = ")[1].strip()
    raise ValueError(f"Could not find vulnbox address in {file}")


@dataclass
class TeamConfigs:
    vulnbox_address: str
    base_path: Path
    vulnbox_filename: str


@dataclass
class VpnInfo:
    server_config_paths: list[Path]
    team_configs: list[TeamConfigs]
    jury_config_path: Path


class WireguardController:
    def __init__(
        self,
        server_address: str,
        vulnbox_port: int,
        team_port: int,
        jury_port: int,
    ):
        self._server_address = server_address
        self._vulnbox_port = vulnbox_port
        self._team_port = team_port
        self._jury_port = jury_port

        self._jury_group = 2

        self._jury_subnet = "10.10.10.0/24"
        self._team_subnet = "10.60.0.0/14"
        self._vulnbox_subnet = "10.80.0.0/14"

        self._jury_group_name = "jury"
        self._team_group_name = "team"
        self._vulnbox_group_name = "vuln"

        self._logger = get_logger("wireguard-controller")

    def generate_configs(
        self,
        total_teams: int,
        per_team: int,
        server_output_dir: Path,
        team_output_dir: Path,
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
            and jury_output_path.exists()
            and all(exists_not_empty(team_output_dir / get_team_dir_name(i)) for i in team_nums)
        ):
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

        tmp_path = Path(tempfile.gettempdir()) / "ad-infra-wireguard"

        tmp_teams_path = tmp_path / "team"
        tmp_vulnbox_path = tmp_path / "vuln"
        for path in [tmp_teams_path, tmp_vulnbox_path]:
            path.mkdir(parents=True, exist_ok=True)

        self._logger.info("Generating team configs")
        team_gen = self._get_generator(
            subnet=self._team_subnet,
            server_number=0,
            server_port=self._team_port,
            groups=team_nums,
            per_group=per_team,
            group_name=self._team_group_name,
        )

        self._logger.info("Generating vulnbox configs")
        vulnbox_gen = self._get_generator(
            subnet=self._vulnbox_subnet,
            server_number=1,
            server_port=self._vulnbox_port,
            groups=team_nums,
            per_group=1,
            group_name=self._vulnbox_group_name,
        )

        self._logger.info("Generating jury config")
        jury_gen = self._get_jury_generator()

        named_generators = {
            "team": team_gen,
            "vuln": vulnbox_gen,
            "jury": jury_gen,
        }

        self._logger.info("Dumping server configs")
        server_configs = []
        for name, gen in named_generators.items():
            assert gen.server_config is not None, f"Server config not generated for '{name}'"
            config_path = server_output_dir / f"{name}_server.conf"
            config_path.write_text(gen.server_config.dumps())
            server_configs.append(config_path)

        self._logger.info("Dumping team configs")
        team_configs = []
        for team_num in team_nums:
            team_dir = team_output_dir / get_team_dir_name(team_num)
            team_dir.mkdir(parents=True, exist_ok=True)

            vulnbox_path = team_dir / f"{self._vulnbox_group_name}{team_num:03}.conf"
            vulnbox_path.write_text(vulnbox_gen.peer_configs[team_num][0].dumps())

            for peer, conf in team_gen.peer_configs[team_num].items():
                config_path = team_dir / f"{self._team_group_name}{team_num:03}_{peer + 1}.conf"
                config_path.write_text(conf.dumps())

            team_configs.append(
                TeamConfigs(
                    vulnbox_address=extract_vulnbox_address(vulnbox_path),
                    base_path=team_dir,
                    vulnbox_filename=vulnbox_path.name,
                )
            )

        self._logger.info("Dumping jury config")
        jury_path = jury_output_path
        jury_path.write_text(jury_gen.peer_configs[self._jury_group][0].dumps())

        self._logger.info("Done")
        return VpnInfo(
            server_config_paths=server_configs,
            team_configs=team_configs,
            jury_config_path=jury_path,
        )

    def _get_generator(
        self,
        subnet: str,
        server_number: int,
        server_port: int,
        groups: list[int],
        per_group: int,
        group_name: str,
    ) -> WGGenerator:
        return WGGenerator(
            server=self._server_address,
            server_number=server_number,
            server_port=server_port,
            per_group=per_group,
            group_list=groups,
            single_peer=False,
            subnet=subnet,
            subnet_newbits=10,
            routed_subnets=",".join(
                [
                    self._jury_subnet,
                    self._team_subnet,
                    self._vulnbox_subnet,
                ]
            ),
            group_name=group_name,
        )

    def _get_jury_generator(self) -> WGGenerator:
        return WGGenerator(
            server=self._server_address,
            server_number=2,
            server_port=self._jury_port,
            group_list=[self._jury_group],
            per_group=1,
            group_name=self._jury_group_name,
            single_peer=True,
            subnet="10.10.10.0/24",
            subnet_newbits=6,
            routed_subnets=",".join(
                [
                    self._jury_subnet,
                    self._team_subnet,
                    self._vulnbox_subnet,
                ]
            ),
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
        for team_dir in map(team_output_dir.joinpath, map(get_team_dir_name, range(total_teams))):
            if team_dir.is_dir():
                vulnbox_filename = list(team_dir.glob(f"{self._vulnbox_group_name}*.conf"))
                msg = f"Expected exactly one vulnbox filename, got {len(vulnbox_filename)}"
                assert len(vulnbox_filename) == 1, msg
                vulnbox_filename = vulnbox_filename[0].name

                team_configs.append(
                    TeamConfigs(
                        base_path=team_dir,
                        vulnbox_filename=vulnbox_filename,
                        vulnbox_address=extract_vulnbox_address(team_dir / vulnbox_filename),
                    )
                )
        return VpnInfo(
            server_config_paths=server_configs,
            team_configs=team_configs,
            jury_config_path=jury_output_path,
        )
