# Taken from https://github.com/pomo-mondreganto/OVPNGen/blob/master/generator.py
# Modified a bit to fit this project better and work with newer versions of dependencies

from pathlib import Path

from constants.paths import (
    VPN_JURY_CLIENT_PATH,
    VPN_JURY_SERVER_PATH,
    vpn_team_client_path,
    vpn_team_server_path,
    vpn_vunlbox_client_path,
    vpn_vunlbox_server_path,
)
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import config, crypto_utils


class ConfigGenerator:
    def __init__(self, vpn_server):
        self.jenv = Environment(
            loader=FileSystemLoader(config.TEMPLATES_PATH),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.vpn_server = vpn_server
        self.ca_cert, self.ca_key = crypto_utils.create_ca(
            cn="cbsctf.live"  # FIXME: should we change this?
        )
        self.dhparam = crypto_utils.get_dhparam()

    @property
    def ca_cert_dump(self):
        return crypto_utils.dump_file_in_mem(self.ca_cert).decode()

    def get_template(self, name):
        return self.jenv.get_template(name)

    def _get_rendered(self, template, client_name, is_server, team_num, static_key):
        cert, key = None, None
        if client_name:
            cert, key = crypto_utils.generate_subnet_certs(
                ca_cert=self.ca_cert,
                ca_key=self.ca_key,
                client_name=client_name,
                serial=0x0C,
                is_server=is_server,
            )

        template = self.get_template(template)
        rendered = template.render(
            config=config,
            server_host=self.vpn_server,
            team_num=team_num,
            ca_cert=self.ca_cert_dump,
            cert=cert,
            key=key,
            static_key=static_key,
            dhparam=self.dhparam,
        )

        return rendered

    @staticmethod
    def _dump_file(rendered, filename: Path):
        with open(filename, "w") as f:
            f.write(rendered)

    @staticmethod
    def format_team_num(team_num):
        return str(team_num).zfill(3)

    def _generate_team(self, team_num, per_team):
        static_key = crypto_utils.generate_static_key()
        formatted_team = self.format_team_num(team_num)

        for player_num in range(1, per_team + 1):
            client_name = f"team{formatted_team}_{player_num}"
            rendered = self._get_rendered(
                template="team_client.j2",
                client_name=client_name,
                is_server=False,
                team_num=team_num,
                static_key=static_key,
            )
            self._dump_file(rendered, vpn_team_client_path(team_num, player_num))

        server_name = f"team_server{formatted_team}"
        rendered = self._get_rendered(
            template="team_server.j2",
            client_name=server_name,
            is_server=True,
            team_num=team_num,
            static_key=static_key,
        )
        self._dump_file(rendered, vpn_team_server_path(team_num))

    def _generate_vuln(self, team_num):
        static_key = crypto_utils.generate_static_key()
        rendered = self._get_rendered(
            template="vuln_client.j2",
            client_name=None,
            is_server=False,
            team_num=team_num,
            static_key=static_key,
        )
        self._dump_file(rendered, vpn_vunlbox_client_path(team_num))

        rendered = self._get_rendered(
            template="vuln_server.j2",
            client_name=None,
            is_server=True,
            team_num=team_num,
            static_key=static_key,
        )
        self._dump_file(rendered, vpn_vunlbox_server_path(team_num))

    def generate_for_teams(self, team_list, per_team):
        for team_num in team_list:
            self._generate_team(team_num, per_team)

    def generate_for_vulns(self, team_list):
        for team_num in team_list:
            self._generate_vuln(team_num)

    def generate_for_jury(self):
        static_key = crypto_utils.generate_static_key()
        rendered = self._get_rendered(
            template="jury_client.j2",
            client_name=None,
            is_server=False,
            team_num=None,
            static_key=static_key,
        )
        self._dump_file(rendered, VPN_JURY_CLIENT_PATH)

        rendered = self._get_rendered(
            template="jury_server.j2",
            client_name=None,
            is_server=True,
            team_num=None,
            static_key=static_key,
        )
        self._dump_file(rendered, VPN_JURY_SERVER_PATH)
