#!/usr/bin/env bash

# Install required packages
apt-get update -qq && apt-get upgrade -qq
apt-get install -qq jq openvpn

# Create accounts for administrators
sed -i -e 's/%sudo\tALL=(ALL:ALL) ALL/%sudo ALL=(ALL) NOPASSWD: ALL/g' /etc/sudoers
curl -s -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/attributes/admin-accounts | jq -c '.[]' | while read -r i; do
    username=$(echo "$i" | jq -r '.username');
    public_ssh_key=$(echo "$i" | jq -r '.public_ssh_key');
    
    useradd -m -G sudo -s /bin/bash "$username"
    mkdir -p "/home/$username/.ssh"
    echo "$public_ssh_key" >> "/home/$username/.ssh/authorized_keys"
    chown -R "$username:$username" "/home/$username"
done
