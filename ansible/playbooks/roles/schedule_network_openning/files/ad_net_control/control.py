#!/usr/bin/env python3

import argparse
import json

import helpers
from config import NetworkConfig, TeamGroup

CONFIG: NetworkConfig

SAME_TEAM_SET = "same-team"
TEAM_VULNBOX_SET = "team-vulnbox"

CLOSED_NET_CHAIN = "closed-network"
OPEN_NET_CHAIN = "open-network"

CLOSED_NETWORK_FORWARDING = ["FORWARD -j closed-network"]
OPEN_NETWORK_FORWARDING = ["FORWARD -j open-network"]


def get_init_rules():
    rules = []

    # Allow already established connections to this machine.
    rules.append("INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT")

    # Drop invalid packets.
    rules.append("INPUT -m conntrack --ctstate INVALID -j DROP")

    # Accept all local connections.
    rules.append("INPUT -i lo -j ACCEPT")

    # Allow ICMP echo requests and replies.
    rules.append("INPUT -p icmp --icmp-type 8 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT")
    rules.append("INPUT -p icmp --icmp-type 0 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT")

    whitelisted_tcp = {22} | set(CONFIG.extra_tcp_ports)
    whitelisted_udp = set(CONFIG.wireguard_ports) | set(CONFIG.extra_udp_ports)

    # Allow connections to whitelisted UDP ports.
    for port in whitelisted_udp:
        rules.append(f"INPUT -p udp --dport {port} -j ACCEPT")

    # Allow connections to whitelisted TCP ports.
    for port in whitelisted_tcp:
        rules.append(f"INPUT -p tcp --dport {port} -j ACCEPT")

    # Allow already established connections, routed through this machine.
    rules.append("FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")

    # Allow access from infra hosts for everyone.
    for host in CONFIG.infra_hosts:
        rules.append(f"FORWARD -s {host.ip} -j ACCEPT")

    # Allow access to always-open infra hosts for everyone.
    for host in CONFIG.infra_hosts:
        if host.always_open:
            rules.append(f"FORWARD -s {host.ip} -j ACCEPT")

    # Always allow traffic from within the same team.
    rules.append(f"FORWARD -m set --match-set {SAME_TEAM_SET} src,dst -j ACCEPT")

    # Configure game interfaces.
    for interface in CONFIG.interface_names:
        # Masquerade everything.
        rules.append(f"POSTROUTING -t nat -o {interface} -j MASQUERADE")

        # Set TTL to 137 to prevent ttl filtering.
        rules.append(f"POSTROUTING -t mangle -o {interface} -j TTL --ttl-set 137")

    # When network is open, allow access to vulnboxes from everywhere.
    rules.append(f"{OPEN_NET_CHAIN} -d {CONFIG.vulnbox_subnet} -j ACCEPT")

    # When network is open, allow traffic to not always-open infra hosts.
    for host in CONFIG.infra_hosts:
        if not host.always_open:
            rules.append(f"{OPEN_NET_CHAIN} -d {host.ip} -j ACCEPT")

    return rules


def configure_sysctl():
    # Allow IPv4 forwarding.
    helpers.set_sysctl("net.ipv4.ip_forward", 1)

    # Increase size of receive, send and aux buffers.
    helpers.set_sysctl("net.core.rmem_max", 1024 * 1024 * 64)  # 64 MB
    helpers.set_sysctl("net.core.wmem_max", 1024 * 1024 * 64)  # 64 MB
    helpers.set_sysctl("net.core.optmem_max", 1024 * 256)  # 256 KB

    # Increase size of conntrack table.
    helpers.set_sysctl("net.netfilter.nf_conntrack_max", 2**20)  # 1M
    helpers.set_sysctl("net.netfilter.nf_conntrack_buckets", 2**18)  # nf_conntrack_max / 4 = 256K


def init_network(args):
    for chain in [CLOSED_NET_CHAIN, OPEN_NET_CHAIN]:
        helpers.create_chain(chain)
        helpers.set_chain_policy(chain, "DROP")

    for s in [SAME_TEAM_SET, TEAM_VULNBOX_SET]:
        helpers.create_set(s)

    init_rules = get_init_rules()
    helpers.add_rules(init_rules)
    helpers.set_chain_policy("INPUT", "DROP")
    helpers.set_chain_policy("FORWARD", "DROP")

    for team in CONFIG.teams:
        helpers.add_to_set(SAME_TEAM_SET, team.team_subnet, team.team_subnet)
        helpers.add_to_set(TEAM_VULNBOX_SET, team.team_subnet, team.vulnbox_ip)

    close_network(args)


def open_network(args):
    helpers.remove_rules(CLOSED_NETWORK_FORWARDING)
    helpers.add_rules(OPEN_NETWORK_FORWARDING)


def close_network(args):
    helpers.remove_rules(OPEN_NETWORK_FORWARDING)
    helpers.add_rules(CLOSED_NETWORK_FORWARDING)


def find_team(vulnbox_ip: str) -> TeamGroup:
    for team in CONFIG.teams:
        if team.vulnbox_ip == vulnbox_ip:
            return team

    raise ValueError(f"Team with vulnbox IP {vulnbox_ip} not found")


def get_ban_rules(team: TeamGroup):
    # Prohibit traffic originating from the team subnet or vulnbox IP.
    return [
        f"FORWARD -s {team.team_subnet} -j DROP",
        f"FORWARD -s {team.vulnbox_ip} -j DROP",
    ]


def ban_team(args):
    team = find_team(args.vulnbox_ip)
    helpers.add_rules(get_ban_rules(team))


def unban_team(args):
    team = find_team(args.vulnbox_ip)
    helpers.remove_rules(get_ban_rules(team))


def add_team_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--vulnbox-ip",
        "-i",
        type=str,
        required=True,
        help="Vulnbox IP of the team",
    )


def main():
    parser = argparse.ArgumentParser(description="Manage network during AD CTF")
    parser.add_argument("--config", "-c", type=str, required=True, help="Path to the config file")

    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser("init", help="Initialize the network")
    init_parser.set_defaults(func=init_network)

    open_parser = subparsers.add_parser("open", help="Open the network")
    open_parser.set_defaults(func=open_network)

    close_parser = subparsers.add_parser("close", help="Close the network")
    close_parser.set_defaults(func=close_network)

    ban_parser = subparsers.add_parser("ban", help="Ban a team")
    ban_parser.set_defaults(func=ban_team)
    add_team_argument(ban_parser)

    unban_parser = subparsers.add_parser("unban", help="Unban a team")
    unban_parser.set_defaults(func=unban_team)
    add_team_argument(unban_parser)

    args = parser.parse_args()
    with open(args.config) as f:
        global CONFIG
        CONFIG = NetworkConfig.from_dict(json.load(f))


if __name__ == "__main__":
    main()
