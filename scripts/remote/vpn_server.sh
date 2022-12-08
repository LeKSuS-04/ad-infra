#!/usr/bin/env bash

# Install dependencies
echo iptables-persistent iptables-persistent/autosave_v4 boolean true | sudo debconf-set-selections
echo iptables-persistent iptables-persistent/autosave_v6 boolean true | sudo debconf-set-selections
sudo apt-get install -qq git python3 python3-pip build-essential libffi-dev zip iptables-persistent at

# Clone OVPNGen and install dependencies
git clone https://github.com/pomo-mondreganto/OVPNGen
cd ~/OVPNGen || exit
sudo pip3 install -q -r requirements.txt

# Fetch configuration variables for OVPNGen
team_data=$(curl -s -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/attributes/teams-config)
team_count=$(echo "$team_data" | jq .team_count)
players_per_team=$(echo "$team_data" | jq .players_per_team)
vpn_server_ip=$(curl -s http://ifconfig.ru)

# Generate VPN configs
sudo ./gen.py --server "$vpn_server_ip" \
    --jury \
    --vuln \
    --team --teams "$team_count" --per-team "$players_per_team"
sudo chown -R "$(whoami):$(whoami)" result

# Pack teams' configs to zip archives
cd ~/OVPNGen/result/team || exit
for team in *; do
    mv "$team" vpn
    zip "$team.zip" vpn/*
    rm -rf vpn
done

# Pack all client configs to single zip archive
cd ~/OVPNGen/result || exit
zip -r clients.zip jury/* team/* vuln/*
rm -rf jury team vuln

# Start VPN servers
cd ~/OVPNGen/result/server || exit
for dir in *; do
    for vpn_config in "$dir"/*; do
        sudo openvpn --config "$vpn_config" --daemon;
    done
done

# Set up net controllers
cd ~ || exit
git clone https://github.com/ne-bknn/ad_net_control
cd ~/ad_net_control || exit
sudo ./net_control.py init --teams "$team_count"

# Schedule network openning and closing
network_data=$(curl -s -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/attributes/network-config)
open_time_unformatted=$(echo "$network_data" | jq -r .open_time)
open_time=$(date -d "$open_time_unformatted" +'%Y%m%d%H%M.%S')
close_time_unformatted=$(echo "$network_data" | jq -r .close_time)
close_time=$(date -d "$close_time_unformatted" +'%Y%m%d%H%M.%S')
timezone=$(echo "$network_data" | jq -r .timezone)

echo "/home/$(whoami)/ad_net_control/net_control.py open --teams $team_count" |\
    TZ=$timezone sudo at -t "$open_time"

echo "/home/$(whoami)/ad_net_control/net_control.py close --teams $team_count" |\
    TZ=$timezone sudo at -t "$close_time"
