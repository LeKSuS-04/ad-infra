#!/usr/bin/env bash

# Copy client configs from vpn server
scp -i "$PRIVATE_KEY_PATH" \
    -o BatchMode=yes \
    -o StrictHostKeychecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o LogLevel=quiet \
    "$USER"@"$HOST":~/OVPNGen/result/clients.zip "$TEMP_DIR/clients.zip"

# Extract client config files from archive
cd "$TEMP_DIR" || exit
unzip clients.zip
rm clients.zip
