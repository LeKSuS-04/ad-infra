#!/usr/bin/env bash

# Install docker
sudo apt-get install -qq gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -qq docker-ce docker-ce-cli containerd.io docker-compose
sudo systemctl start docker

# Fetch configuration variables from metadata
data=$(curl -s -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/attributes/?recursive=True)

# Fetch vulnbox number from metadata
team_number=$(echo "$data" | jq -r '."team-number"')

# Create team user
username="team$(printf '%03d' "$team_number")";
password=$(echo "$data" | jq -r .password)
sudo useradd -m -G sudo -s /bin/bash "$username"
sudo chpasswd <<< "$username:$password"

# Get bucket with files
bucket=$(echo "$data" | jq -r '.bucket')

# Extract vpn config from bucket
cd ~ || exit
vpn_config_key=$(echo "$data" | jq -r '."vpn-config-key"')
sudo wget "https://storage.yandexcloud.net/$bucket/$vpn_config_key" -O /root/config.ovpn

# Connect to vpn network
sudo openvpn --config /root/config.ovpn --daemon

# Fetch zip with services to teamXXX account
services_key=$(echo "$data" | jq -r '."services-resource-key"')
sudo wget "https://storage.yandexcloud.net/$bucket/$services_key" -O "/home/$username/services.zip"

# Extract services 
mkdir -p ~/services
sudo unzip "/home/$username/services.zip" -d "/home/$username/services"
sudo chown -R "$username":"$username" "/home/$username"

for compose_file in /home/"$username"/services/*/docker-compose.*; do
    sudo docker-compose -f "$compose_file" up -d
done

# Don't allow direct connections from other vulnboxes
interface_data=$(ip route | grep eth0)
ips=$(echo "$interface_data" | sed 's/.*via //g' | sed 's/ dev.*//g')
mapfile -t separeted <<< "$ips"
gateway=${separeted[0]}
# shellcheck disable=SC2001
dns_server=$(echo "$gateway" | sed 's/.1$/.2/g')
mask=${separeted[1]}
sudo iptables -A INPUT -s "$gateway" -j ACCEPT
sudo iptables -A INPUT -s "$dns_server" -j ACCEPT
sudo iptables -A INPUT -s "$mask" -j REJECT
sudo iptables -A OUTPUT -d "$gateway" -j ACCEPT
sudo iptables -A OUTPUT -d "$dns_server" -j ACCEPT
sudo iptables -A OUTPUT -d "$mask" -j REJECT
