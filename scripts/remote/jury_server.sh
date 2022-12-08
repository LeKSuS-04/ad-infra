#!/usr/bin/env bash

# Install dependencies
sudo apt-get install -qq git python3 python3-pip zip
sudo wget "https://github.com/mikefarah/yq/releases/download/v4.2.0/yq_linux_amd64.tar.gz" -O - |\
    sudo tar xz && sudo mv "yq_linux_amd64" /usr/bin/yq

# Install docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -qq docker-ce docker-ce-cli containerd.io docker-compose
sudo systemctl start docker

# Connect to vpn network
sudo mv config.ovpn /root/config.ovpn
sudo openvpn --config /root/config.ovpn --daemon

# Clone forcad repo
git clone https://github.com/pomo-mondreganto/ForcAD

# Extract checkers from archive
mkdir -p ~/ForcAD/checkers
mv ./checkers.zip ~/ForcAD/checkers
cd ~/ForcAD/checkers || exit
unzip -o checkers.zip
rm checkers.zip

# Write forcad configuration
cd ~/ForcAD || exit
curl -s -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/attributes/forcad-config |\
    yq e -MP > config.yml

# Deploy forcad
cd ~/ForcAD || exit
sudo pip3 install -q -r cli/requirements.txt
sudo ./control.py setup
sudo ./control.py start --fast

# Extract and pack team tokens
mkdir -p ~/ForcAD/tokens
cd ~/ForcAD || exit
# Tokens aren't available immediately, we need to give forcad some time to wake up
set -o pipefail
until team_tokens=$(sudo ./control.py print_tokens 2>/dev/null | sed -r 's/[ ]{1}/_/g'); do
  echo "Team tokens aren't available yet, going to retry in 5 seconds..."
  sleep 5
done
# Separate team tokens from team names
for team_token in $team_tokens; do
  token=$(echo "$team_token" | rev | cut -d ':' -f 1 | rev);
  team=${team_token%":$token"}
  echo "$token" > "$HOME/ForcAD/tokens/${team}.txt"
done
cd tokens || exit
zip tokens.zip ./*
rm -rf ./*.txt
