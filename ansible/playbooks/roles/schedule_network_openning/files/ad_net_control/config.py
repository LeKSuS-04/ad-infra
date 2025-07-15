from dataclasses import dataclass


@dataclass
class TeamGroup:
    vulnbox_ip: str
    team_subnet: str

    @classmethod
    def from_dict(cls, data: dict) -> "TeamGroup":
        return cls(
            vulnbox_ip=data["vulnbox_ip"],
            team_subnet=data["team_subnet"],
        )

    def to_dict(self) -> dict:
        return {
            "vulnbox_ip": self.vulnbox_ip,
            "team_subnet": self.team_subnet,
        }


@dataclass
class InfraHost:
    ip: str
    always_open: bool

    @classmethod
    def from_dict(cls, data: dict) -> "InfraHost":
        return cls(
            ip=data["ip"],
            always_open=data.get("always_open", False),
        )

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "always_open": self.always_open,
        }


@dataclass
class NetworkConfig:
    wireguard_ports: list[int]
    interface_names: list[str]
    infra_hosts: list[InfraHost]
    vulnbox_subnet: str
    teams: list[TeamGroup]
    extra_tcp_ports: list[int]
    extra_udp_ports: list[int]

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkConfig":
        return cls(
            wireguard_ports=data["listener_ports"],
            interface_names=data["interface_names"],
            infra_hosts=[InfraHost.from_dict(host) for host in data["infra_hosts"]],
            vulnbox_subnet=data["vulnbox_subnet"],
            teams=[TeamGroup.from_dict(team) for team in data["teams"]],
            extra_tcp_ports=data.get("extra_tcp_ports", []),
            extra_udp_ports=data.get("extra_udp_ports", []),
        )

    def to_dict(self) -> dict:
        return {
            "wireguard_ports": self.wireguard_ports,
            "interface_names": self.interface_names,
            "infra_hosts": [host.to_dict() for host in self.infra_hosts],
            "vulnbox_subnet": self.vulnbox_subnet,
            "teams": [team.to_dict() for team in self.teams],
            "extra_tcp_ports": self.extra_tcp_ports,
            "extra_udp_ports": self.extra_udp_ports,
        }
