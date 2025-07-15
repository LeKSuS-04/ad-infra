import subprocess
from dataclasses import dataclass
from math import ceil, log2
from typing import Any

from netaddr import IPNetwork
from util.iterutil import skip_n, take_n


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
    def __init__(
        self,
        name: str,
        values: dict[str, Any],
        comment: str | None = None,
    ):
        self.name = name
        self.values = values
        self.comment = comment

    def dumps(self):
        headers = f"[{self.name}]\n"
        comment = f"#comment {self.comment}\n" if self.comment else ""
        content = "\n".join(f"{k} = {v}" for k, v in self.values.items())
        return headers + comment + content


class WGConfig:
    def __init__(
        self,
        sections: list[ConfigSection] | None = None,
        values: dict[str, Any] | None = None,
    ):
        self.sections = sections or []
        self.values = values or {}

    def add_section(self, section: ConfigSection):
        self.sections.append(section)

    def dumps(self):
        return "\n\n".join(s.dumps() for s in self.sections)


@dataclass
class NetworkConfigs[T]:
    server_config: WGConfig
    peer_configs: dict[T, WGConfig]


def generate_const_network[T](
    server_host: str,
    server_port: int,
    server_vpn_address: IPNetwork,
    peer_addresses: dict[T, IPNetwork],
    routed_subnets: list[IPNetwork],
) -> NetworkConfigs[T]:
    assert server_vpn_address.prefixlen == 32, "server address must be /32"
    for peer, peer_subnet in peer_addresses.items():
        assert peer_subnet.prefixlen == 32, f"peer {peer} must be /32"

    server_key = WGKey.generate()
    server_config = WGConfig(
        sections=[
            ConfigSection(
                name="Interface",
                values={
                    "Address": str(server_vpn_address[1]),
                    "PrivateKey": server_key.private,
                    "ListenPort": server_port,
                },
            )
        ]
    )

    peer_configs: dict[T, WGConfig] = {}
    for peer_id, peer_address in peer_addresses.items():
        peer_key = WGKey.generate()
        server_config.add_section(
            ConfigSection(
                name="Peer",
                values={
                    "PublicKey": peer_key.public,
                    "AllowedIPs": str(peer_address),
                },
                comment=f"friendly_name = {peer_key}",
            )
        )

        peer_configs[peer_id] = WGConfig(
            sections=[
                ConfigSection(
                    name="Interface",
                    values={
                        "Address": str(peer_address[0]),
                        "PrivateKey": peer_key.private,
                    },
                ),
                ConfigSection(
                    name="Peer",
                    values={
                        "PublicKey": server_key.public,
                        "Endpoint": f"{server_host}:{server_port}",
                        "AllowedIPs": ",".join(map(str, routed_subnets)),
                    },
                ),
            ],
            values={
                "PersistentKeepalive": 25,
            },
        )

    return NetworkConfigs(server_config=server_config, peer_configs=peer_configs)


@dataclass
class Group:
    subnet: IPNetwork
    peers: list[WGConfig]


@dataclass
class GroupConfigs[T]:
    server_config: WGConfig
    peer_configs: dict[T, Group]


def generate_group_network[T](
    group_name: str,
    subnet: IPNetwork,
    routed_subnets: list[IPNetwork],
    server_host: str,
    server_port: int,
    groups: list[T],
    bits_per_group: int,
    peers_per_group: int,
    peer_offset: int,
) -> GroupConfigs[T]:
    assert peer_offset + peers_per_group <= 254, "not enough bits for peers within group"
    assert 24 - subnet.prefixlen > ceil(log2(len(groups) + 2)), "not enough bits for all groups"

    server_key = WGKey.generate()
    server_config = WGConfig(
        sections=[
            ConfigSection(
                name="Interface",
                values={
                    "Address": str(subnet[1]),
                    "PrivateKey": server_key.private,
                    "ListenPort": server_port,
                },
            )
        ]
    )

    peer_configs: dict[T, Group] = {}
    group_subnets = skip_n(subnet.subnet(24), 1)
    for group_id, group_subnet in zip(groups, group_subnets):
        peer_subnets = skip_n(group_subnet.subnet(32), 1 + peer_offset)
        peers = []
        for peer_subnet in take_n(peer_subnets, peers_per_group):
            peer_key = WGKey.generate()

            server_config.add_section(
                ConfigSection(
                    name="Peer",
                    values={
                        "PublicKey": peer_key.public,
                        "AllowedIPs": str(peer_subnet),
                    },
                    comment=f"friendly_name = {group_name}{group_id}",
                )
            )

            peer_config = WGConfig(
                sections=[
                    ConfigSection(
                        name="Interface",
                        values={
                            "Address": str(peer_subnet[0]),
                            "PrivateKey": peer_key.private,
                        },
                    ),
                    ConfigSection(
                        name="Peer",
                        values={
                            "PublicKey": server_key.public,
                            "Endpoint": f"{server_host}:{server_port}",
                            "AllowedIPs": ",".join(map(str, routed_subnets)),
                        },
                    ),
                ],
                values={
                    "PersistentKeepalive": 25,
                },
            )
            peers.append(peer_config)

        peer_configs[group_id] = Group(subnet=group_subnet, peers=peers)

    return GroupConfigs(server_config=server_config, peer_configs=peer_configs)
